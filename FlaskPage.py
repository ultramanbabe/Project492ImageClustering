from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
from werkzeug.utils import secure_filename
import datetime
from pymongo import MongoClient
from Clustering_using_Model import cluster_images
from collections import defaultdict
from datetime import datetime


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
                images.insert_one({'path': file_path, 'upload_time': datetime.now()})

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


@app.route('/delete_cluster', methods=['POST'])
def delete_cluster():
    # Get the cluster ID from the form data
    cluster_id = request.form.get('cluster_id')

    # Construct the path to the cluster
    cluster_path = os.path.join('static', 'clustered_images', cluster_id)

    # Delete the cluster
    shutil.rmtree(cluster_path)

    # Redirect the user back to the manage_clusters page
    return redirect(url_for('manage_clusters'))


@app.route('/delete_folder/<folder_name>', methods=['POST'])
def delete_folder(folder_name):
    folder_path = os.path.join('static', 'uploads', folder_name)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        # Delete the documents from MongoDB
        escaped_folder_path = folder_path.replace('\\', '\\\\')
        images.delete_many({'path': {'$regex': '^' + escaped_folder_path}})
    return redirect(url_for('upload_file'))


@app.route('/delete_subfolder', methods=['POST'])
def delete_subfolder():
    # Get the cluster ID and the subfolder name from the form data
    cluster_id = request.form.get('cluster_id')
    subfolder = request.form.get('subfolder')

    # Construct the path to the subfolder
    subfolder_path = os.path.join('static', 'clustered_images', cluster_id, subfolder)

    # Delete the subfolder
    shutil.rmtree(subfolder_path)

    # Redirect the user back to the view_cluster page
    return redirect(url_for('view_cluster', cluster_id=cluster_id))


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


@app.route('/cluster/<path:cluster_id>')
def view_cluster(cluster_id):
    # Get a list of all subfolders and their images in the cluster
    cluster_dir = os.path.join('static', 'clustered_images', cluster_id)
    subfolders = [d for d in os.listdir(cluster_dir) if os.path.isdir(os.path.join(cluster_dir, d))]
    subfolder_images = {subfolder: os.listdir(os.path.join(cluster_dir, subfolder)) for subfolder in subfolders}

    # Render a template and pass the list of subfolders and their images to it
    return render_template('view_cluster.html', cluster_id=cluster_id, subfolder_images=subfolder_images)


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
            
    # clusters = os.listdir(os.path.join('static', 'clustered_images'))
    cluster_ids = os.listdir(os.path.join('static', 'clustered_images'))

    return render_template('manage_clusters.html', cluster_ids=cluster_ids)


@app.route('/manage_subfolder', methods=['POST'])
def manage_subfolder():
    # Get the action, cluster ID, subfolder name, and input value from the form data
    action = request.form.get('action')
    cluster_id = request.form.get('cluster_id')
    subfolder = request.form.get('subfolder')
    target_subfolder_name = request.form.get('cluster_id_input')

    # Construct the path to the subfolder
    subfolder_path = os.path.join('static', 'clustered_images', cluster_id, subfolder)

    if action == 'delete':
        # Delete the subfolder
        shutil.rmtree(subfolder_path)
    elif action == 'merge':
        # Merge the subfolder with another subfolder
        merge_subfolder(cluster_id, subfolder, target_subfolder_name)
    elif action == 'rename':
        # Rename the subfolder
        rename_subfolder(subfolder_path, target_subfolder_name)

    # Redirect the user back to the view_cluster page
    return redirect(url_for('view_cluster', cluster_id=cluster_id))


def merge_subfolder(cluster_id, source_subfolder_name, target_subfolder_name):
    # Construct the paths to the source and target subfolders
    source_subfolder_path = os.path.join('static', 'clustered_images', cluster_id, source_subfolder_name)
    target_subfolder_path = os.path.join('static', 'clustered_images', cluster_id, target_subfolder_name)

    # Move all files from the source subfolder to the target subfolder
    for filename in os.listdir(source_subfolder_path):
        shutil.move(os.path.join(source_subfolder_path, filename), target_subfolder_path)

    # Delete the source subfolder
    shutil.rmtree(source_subfolder_path)


def rename_subfolder(subfolder_path, new_subfolder_name):
    # Get the parent directory
    parent_dir = os.path.dirname(subfolder_path)

    # Construct the path to the new subfolder
    new_subfolder_path = os.path.join(parent_dir, new_subfolder_name)

    # Rename the subfolder
    os.rename(subfolder_path, new_subfolder_path)


@app.route('/summary')
def summary():
    # Get the path to the clustered_images directory
    clustered_images_path = 'static/clustered_images'

    # Initialize a dictionary to store the number of subfolders created each day
    subfolders_per_day = defaultdict(int)

    # Initialize a dictionary to store some image paths for each day
    example_images_per_day = defaultdict(list)

    # Iterate over all clusters
    for cluster_id in os.listdir(clustered_images_path):
        cluster_path = os.path.join(clustered_images_path, cluster_id)

        # Convert the cluster ID to a date
        taken_date = datetime.strptime(cluster_id, '%d-%m-%Y').date()

        # Iterate over all subfolders in the cluster
        for subfolder in os.listdir(cluster_path):
            subfolder_path = os.path.join(cluster_path, subfolder)

            # Increment the count of subfolders created on this date
            subfolders_per_day[taken_date] += 1

            # Get some image paths from the subfolder
            image_paths = [os.path.join('clustered_images', cluster_id, subfolder, image).replace('\\', '/') for image in os.listdir(subfolder_path)[:5]]
            example_images_per_day[taken_date].extend(image_paths)

    # Sort the dictionaries by date
    subfolders_per_day = dict(sorted(subfolders_per_day.items()))

    # Sort the images in each day by time
    for date, images in example_images_per_day.items():
        example_images_per_day[date] = sorted(images, key=lambda image: image.split('-')[-1].split('.')[0])

    # Render the summary template
    return render_template('summary.html', subfolders_per_day=subfolders_per_day, example_images_per_day=example_images_per_day)




app.run(debug=True, port=5000)