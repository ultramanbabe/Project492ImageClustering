from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
from werkzeug.utils import secure_filename
import datetime
from pymongo import MongoClient
from Clustering_using_Model import cluster_images


client = MongoClient('localhost', 27017)    # Connect to the MongoDB server
db = client['images']    # Create a database called images
images = db['images']
clustered_images = db['clustered_images']

app = Flask(__name__)


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        for file in request.files.getlist('file'):

            if file and file.filename.endswith('.jpg'):
                # Get the name of the uploaded folder
                uploaded_folder = os.path.dirname(file.filename)

                # Create a new directory with the same name as the uploaded folder
                upload_path = os.path.join('static', 'uploads', secure_filename(uploaded_folder))
                os.makedirs(upload_path, exist_ok=True)

                # Save the file in the new directory
                filename = secure_filename(os.path.basename(file.filename))
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)

                # Insert the image path and upload time into MongoDB
                images.insert_one({'path': file_path, 'upload_time': datetime.datetime.now()})

    # Rest of your code...

    # Get a list of the uploaded directories
    uploads = os.listdir(os.path.join('static', 'uploads'))

    # Get a dictionary where the keys are the folder names and the values are the image file paths
    images_dict = {}
    for upload in uploads:
        images_dict[upload] = []
        for filename in os.listdir(os.path.join('static', 'uploads', upload).replace('\\', '/')): 
            if filename.endswith('.jpg') or filename.endswith('.png'):
                # Include only the part of the path that comes after 'static/uploads/'
                images_dict[upload].append(os.path.join(upload, filename).replace('\\', '/'))
    

    return render_template('upload.html', images=images_dict)



@app.route('/delete_folder/<folder_name>', methods=['POST'])
def delete_folder(folder_name):
    folder_path = os.path.join('static', 'uploads', folder_name)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        # Delete the documents from MongoDB
        escaped_folder_path = folder_path.replace('\\', '\\\\')
        images.delete_many({'path': {'$regex': '^' + escaped_folder_path}})
    return redirect(url_for('upload_file'))


@app.route('/create_cluster/<folder_name>', methods=['POST'])
def create_cluster(folder_name):
    # Cluster the images using the model 
    cluster_images(folder_name)

    # Check if there are already clustered images for the folder
    clustered_folder_path = os.path.join('static', 'clustered_images', folder_name)
    if os.path.exists(clustered_folder_path):
        # Remove the original folder
        shutil.rmtree(os.path.join('static', 'uploads', folder_name))

    return redirect(url_for('upload_file'))


@app.route('/manage_clusters', methods=['GET', 'POST'])
def manage_clusters():
    if request.method == 'POST':
        action = request.form.get('action')
        cluster_id = request.form.get('cluster_id')

        if action == 'delete':
            # Delete the cluster
            shutil.rmtree(os.path.join('static', 'clustered_images', cluster_id))

        elif action == 'merge':
            # Merge clusters
            target_cluster_id = request.form.get('target_cluster_id')
            source_dir = os.path.join('static', 'clustered_images', cluster_id)
            target_dir = os.path.join('static', 'clustered_images', target_cluster_id)
            for filename in os.listdir(source_dir):
                shutil.move(os.path.join(source_dir, filename), target_dir)
            shutil.rmtree(source_dir)

        elif action == 'rename':
            # Rename cluster
            new_name = request.form.get('new_cluster_id')
            if new_name is not None:
                old_path = os.path.join('static', 'clustered_images', cluster_id)
                new_path = os.path.join('static', 'clustered_images', new_name)
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
            
    clusters = os.listdir(os.path.join('static', 'clustered_images').replace('\\', '/'))

    return render_template('manage_clusters.html', clusters=clusters)


@app.route('/summary')
def summary():
    return render_template('summary')

app.run(debug=True, port=5000)