import telebot
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

bot = telebot.TeleBot('6940974472:AAGHab8t3tMFAOzQtpLhERMHgFUuEbtFDOw')

# Dictionary untuk menyimpan daftar task
tasks = {}

# Fungsi untuk menampilkan daftar task dalam bentuk gambar
def show_tasks_image(chat_id):
    img = Image.new('RGB', (500, 500), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 20)

    # Menyiapkan teks untuk gambar
    task_list = [f"Task: {task}\nDeadline: {details['deadline']}" for task, details in tasks.items()]
    task_text = "\n\n".join(task_list)

    draw.text((10, 10), f"Daftar Task:\n\n{task_text}", fill='black', font=font)

    # Simpan gambar sebagai file PNG
    image_path = 'task_list.png'
    img.save(image_path)
    bot.send_photo(chat_id, open(image_path, 'rb'))

# Fungsi untuk menangani command /start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, 'Halo bro, ada apa?')

# Fungsi untuk menangani command /task
@bot.message_handler(commands=['task'])
def set_task(message):
    bot.reply_to(message, 'Masukkan nama task:')
    @bot.message_handler(func=lambda m: True)
    def capture_task_name(message):
        try:
            task_name = message.text
            tasks[task_name] = {'deadline': ''}
            bot.send_message(message.chat.id, 'Masukkan deadline (contoh: 2023-12-31 23:59):')
            bot.register_next_step_handler(message, capture_deadline, task_name)
        except Exception as e:
            bot.send_message(message.chat.id, f'Terjadi kesalahan: {e}')

# Fungsi untuk menangkap deadline task
def capture_deadline(message, task_name):
    try:
        deadline = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        tasks[task_name]['deadline'] = deadline.strftime('%Y-%m-%d %H:%M:%S')
        bot.send_message(message.chat.id, f"Task '{task_name}' dengan deadline {tasks[task_name]['deadline']} berhasil disimpan!")
        show_tasks_image(message.chat.id)
    except ValueError:
        bot.reply_to(message, 'Format deadline tidak valid! Gunakan format: YYYY-MM-DD HH:MM')

# Fungsi untuk menangani command /set_reminder
@bot.message_handler(commands=['set_reminder'])
def set_reminder(message):
    # Membuat job untuk mengirim daftar task setiap interval 1 jam
    @bot.message_handler(func=lambda m: True)
    def send_tasks_reminder(message):
        if datetime.now().minute == 0:  # Memeriksa apakah sudah tepat jam untuk mengirimkan reminder
            for chat_id in tasks:
                show_tasks_image(chat_id)
            bot.reply_to(message, 'Daftar task telah dikirimkan ke pengguna setiap interval 1 jam.')

# Jalankan bot
if __name__ == '__main__':
    bot.polling()
