from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
# dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
# os.makedirs(dir_path, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        for file in request.files.getlist('file'):
            if file and file.filename.endswith('.jpg'):
                # Create a new directory for the uploaded file
                dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'uploads')
                new_dir_path = os.path.join(dir_path, secure_filename(os.path.basename(file.filename)))
                os.makedirs(new_dir_path, exist_ok=True)

                # Save the file in the new directory
                file.save(os.path.join(new_dir_path, secure_filename(os.path.basename(file.filename))))
        return redirect(url_for('manage_clusters'))
    return render_template('upload.html')

@app.route('/view_uploads/<folder>')
def view_folder_uploads(folder):
    # Get a list of the image file paths in the specified folder
    image_paths = []
    folder_path = os.path.join('static', 'uploads', folder)
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image_paths.append(os.path.join('uploads', folder, filename))

    # Render the view_uploads template and pass the image paths to it
    return render_template('view_uploads.html', image_paths=image_paths)

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
            shutil.rmtree(os.path.join('dbscan_clustered_images', cluster_id))

    return render_template('manage_clusters.html')