from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(dir_path, filename))
            return redirect(url_for('manage_clusters'))
    return render_template('upload.html')

@app.route('/manage_clusters', methods=['GET', 'POST'])
def manage_clusters():
    # Your existing code to extract features and cluster images
    # ...

    # Return a response to the user
    return render_template('manage_clusters.html', clusters=clusters)

@app.route('/summary')
def summary():
    # Your existing code to generate the summary
    # ...

    # Return a response to the user
    return render_template('summary.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)