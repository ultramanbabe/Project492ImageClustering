from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
# dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
# os.makedirs(dir_path, exist_ok=True)


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Get the name of the uploaded folder
        uploaded_folder = request.files['file'].filename.split('/')[0]

        # Create a new directory with the same name as the uploaded folder
        upload_path = os.path.join('static', 'uploads', secure_filename(uploaded_folder))
        os.makedirs(upload_path, exist_ok=True)

        # Save all files in the new directory
        for file in request.files.getlist('file'):
            if file and file.filename.endswith('.jpg'):
                file.save(os.path.join(upload_path, secure_filename(file.filename)))

    return render_template('upload.html')

@app.route('/view_uploads')
def view_uploads():
    # Get a list of the uploaded directories
    uploads = os.listdir(os.path.join('static', 'uploads'))

    # Get a dictionary where the keys are the folder names and the values are the image file paths
    images = {}
    for upload in uploads:
        images[upload] = []
        for filename in os.listdir(os.path.join('static', 'uploads', upload).replace('\\', '/')): 
            if filename.endswith('.jpg') or filename.endswith('.png'):
                images[upload].append(os.path.join('uploads', upload, filename).replace('\\', '/'))
                #replace('\\', '/') is used to replace the backslash with forward slash in the file path to avoid path conflict in windows
    # Render the view_uploads template and pass the images dictionary to it
    return render_template('view_uploads.html', images=images)

@app.route('/choose_model')
def choose_model():
    return render_template('choose_model.html')

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