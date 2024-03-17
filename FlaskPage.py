from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__)
dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
os.makedirs(dir_path, exist_ok=True)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file:
                # Extract the directory name from the file path
                directory = os.path.dirname(file.filename)

                # Create a new directory in the upload location
                new_dir_path = os.path.join(dir_path, secure_filename(directory))
                os.makedirs(new_dir_path, exist_ok=True)

                # Save the file in the new directory
                file.save(os.path.join(new_dir_path, secure_filename(os.path.basename(file.filename))))
        return redirect(url_for('manage_clusters'))
    return render_template('upload.html')

@app.route('/choose_model')
def choose_model():
    return render_template('choose_model.html')

@app.route('/manage_clusters', methods=['GET', 'POST'])
def manage_clusters():
    def manage_clusters():
        if request.method == 'POST':
            action = request.form.get('action')
            cluster_id = request.form.get('cluster_id')

            if action == 'delete':
                # Delete the cluster
                shutil.rmtree(os.path.join('dbscan_clustered_images', cluster_id))
            elif action == 'merge':
                # Merge the cluster with another cluster
                target_cluster_id = request.form.get('target_cluster_id')
                for filename in os.listdir(os.path.join('dbscan_clustered_images', cluster_id)):
                    shutil.move(os.path.join('dbscan_clustered_images', cluster_id, filename),
                                os.path.join('dbscan_clustered_images', target_cluster_id))
                os.rmdir(os.path.join('dbscan_clustered_images', cluster_id))
            elif action == 'rename':
                # Rename the cluster
                new_cluster_id = request.form.get('new_cluster_id')
                os.rename(os.path.join('dbscan_clustered_images', cluster_id),
                        os.path.join('dbscan_clustered_images', new_cluster_id))

    # Get the current list of clusters
    clusters = os.listdir('dbscan_clustered_images')
    return render_template('manage_clusters.html', clusters=clusters)

@app.route('/summary')
def summary():
    # Your existing code to generate the summary
    # ...

    # Return a response to the user
    return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)