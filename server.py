from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import datetime
import json
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Rsool1388Secret!'
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
CORS(app)

# ساخت پوشه‌ها
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path('/tmp/data').mkdir(parents=True, exist_ok=True)

# رمز گروه
GROUP_PASSWORD = generate_password_hash("Rsool.1388")

# دیتابیس فایل‌ها
FILES_DB = '/tmp/data/files.json'

def load_files():
    try:
        if os.path.exists(FILES_DB):
            with open(FILES_DB, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_files(files):
    try:
        with open(FILES_DB, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving files: {e}")

# صفحه اصلی
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>سرور گروه</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Vazir', Tahoma, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
                width: 90%;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 2.5em;
            }
            .status {
                background: #4caf50;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 1.2em;
            }
            .info {
                background: #f0f0f0;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .info p {
                margin: 10px 0;
                color: #555;
            }
            .emoji {
                font-size: 4em;
                margin: 20px 0;
            }
            code {
                background: #333;
                color: #4caf50;
                padding: 5px 10px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🚀</div>
            <h1>سرور فعال است!</h1>
            <div class="status">✅ همه‌چیز درست کار می‌کنه</div>
            <div class="info">
                <p><strong>نسخه:</strong> 1.0.0</p>
                <p><strong>رمز گروه:</strong> <code>Rsool.1388</code></p>
                <p><strong>تعداد فایل‌ها:</strong> ''' + str(len(load_files())) + '''</p>
                <p><strong>وضعیت:</strong> آماده دریافت درخواست</p>
            </div>
            <p style="color: #888; margin-top: 30px;">
                برای استفاده، این آدرس رو در اپلیکیشن وارد کنید
            </p>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

# API: لاگین
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if check_password_hash(GROUP_PASSWORD, password):
            return jsonify({
                'success': True,
                'username': username,
                'message': 'خوش آمدید!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'رمز اشتباه است!'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# API: آپلود فایل
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'فایلی انتخاب نشده'}), 400
        
        file = request.files['file']
        username = request.form.get('username', 'ناشناس')
        
        if file and file.filename:
            # ذخیره فایل
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # اطلاعات فایل
            file_info = {
                'id': timestamp,
                'original_name': file.filename,
                'filename': unique_filename,
                'uploader': username,
                'date': datetime.datetime.now().strftime('%Y/%m/%d'),
                'time': datetime.datetime.now().strftime('%H:%M:%S'),
                'size': os.path.getsize(filepath),
                'type': file.content_type or 'application/octet-stream'
            }
            
            # ذخیره در دیتابیس
            files = load_files()
            files.append(file_info)
            save_files(files)
            
            return jsonify({
                'success': True,
                'message': 'فایل با موفقیت آپلود شد!',
                'file': file_info
            })
        
        return jsonify({'success': False, 'error': 'خطا در آپلود'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API: لیست فایل‌ها
@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        files = load_files()
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API: دانلود فایل
@app.route('/api/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'فایل یافت نشد'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: حذف فایل
@app.route('/api/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        files = load_files()
        updated_files = []
        deleted = False
        
        for file in files:
            if file['id'] == file_id:
                # حذف فایل فیزیکی
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file['filename'])
                if os.path.exists(filepath):
                    os.remove(filepath)
                deleted = True
            else:
                updated_files.append(file)
        
        if deleted:
            save_files(updated_files)
            return jsonify({'success': True, 'message': 'فایل حذف شد'})
        else:
            return jsonify({'success': False, 'message': 'فایل یافت نشد'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# تست API
@app.route('/api/test')
def test():
    return jsonify({
        'status': 'OK',
        'time': datetime.datetime.now().isoformat(),
        'message': 'سرور در حال اجراست!'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
