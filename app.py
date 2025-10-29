import os
import sys
import subprocess
import platform
import time
from yt_dlp import YoutubeDL
import pyfiglet
from colorama import Fore, Style

def print_with_delay(text, delay=0.5):
    """Matnni chiqarib va keyin kutish"""
    print(text)
    time.sleep(delay)

def check_and_install_requirements():
    """Kerakli dasturlar va kutubxonalarni tekshirish va o'rnatish"""
    print_with_delay("🔍 Kerakli komponentlar tekshirilmoqda...", 1)

    required_packages = ['yt-dlp', 'pyfiglet', 'colorama']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'yt-dlp':
                import yt_dlp
            elif package == 'pyfiglet':
                import pyfiglet
            elif package == 'colorama':
                import colorama
            print_with_delay(f"✅ {package} - mavjud", 0.3)
        except ImportError:
            missing_packages.append(package)
            print_with_delay(f"❌ {package} - topilmadi", 0.3)

    if missing_packages:
        print_with_delay(f"\n📦 {len(missing_packages)} ta kutubxona o'rnatilmoqda...", 1)
        for package in missing_packages:
            try:
                print_with_delay(f"🔄 {package} o'rnatilmoqda...", 0.5)
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print_with_delay(f"✅ {package} - muvaffaqiyatli o'rnatildi", 0.5)
            except subprocess.CalledProcessError:
                print_with_delay(f"❌ {package} - o'rnatish muvaffaqiyatsiz", 0.5)
                return False

    print_with_delay("\n🎬 FFmpeg tekshirilmoqda...", 1)
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print_with_delay("✅ FFmpeg - mavjud", 0.5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_with_delay("❌ FFmpeg - topilmadi", 0.5)
        return install_ffmpeg_safe()

def install_ffmpeg_safe():
    """Xavfsiz FFmpeg o'rnatish usuli"""
    system = platform.system().lower()
    print_with_delay(f"\n📥 FFmpeg o'rnatilmoqda ({system})...", 1)

    if system == "linux":
        try:
            print_with_delay("🔄 Repositorylar yangilanmoqda...", 2)

            result = subprocess.run([
                'sudo', 'apt', 'install', '-y', 'ffmpeg',
                '--allow-unauthenticated', '--fix-broken'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print_with_delay("✅ FFmpeg muvaffaqiyatli o'rnatildi", 1)
                return True
            else:
                try:
                    subprocess.run(['sudo', 'snap', 'install', 'ffmpeg'], check=True)
                    print_with_delay("✅ FFmpeg Snap orqali muvaffaqiyatli o'rnatildi", 1)
                    return True
                except:
                    return False

        except subprocess.CalledProcessError:
            return False
    return False

def setup_directories():
    """Kerakli papkalarni yaratish"""
    DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(DOWNLOADS_DIR):
        print_with_delay("📁 Yuklab olish papkasi yaratilmoqda...", 1)
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        print_with_delay(f"✅ Papka yaratildi: {DOWNLOADS_DIR}", 0.5)
    return DOWNLOADS_DIR

def show_banner():
    """Banner va start animatsiya"""
    print_with_delay("🚀 Dastur ishga tushmoqda...", 1)

    for i in range(3):
        print_with_delay("⏳ " + "." * (i + 1), 0.5)

    banner = pyfiglet.figlet_format("Free YouTube", font="slant")
    print(Fore.BLUE + banner)
    print(Fore.MAGENTA + "Created by BlackHole Team" + Style.RESET_ALL)

    print_with_delay("🎯 BEPUL YouTube Downloader - 100% Open Source!", 1)
    print_with_delay("📹 144p dan 8K gacha barcha formatlar qo'llab-quvvatlanadi!", 0.5)
    print_with_delay("💸 Hech qanday to'lov yoki cheklovlar yo'q!", 0.5)

def get_available_formats(url, mode="video"):
    """Mavjud formatlarni olish"""
    ydl_opts = {'quiet': True, 'no_warnings': True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            if mode == "video":
                # Video formatlarini saralash
                video_formats = []
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        video_formats.append(f)

                # Sifat bo'yicha tartiblash
                quality_order = ['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
                sorted_formats = []

                for quality in quality_order:
                    for f in video_formats:
                        if f.get('format_note') == quality:
                            sorted_formats.append(f)

                # Qolgan formatlar
                for f in video_formats:
                    if f not in sorted_formats and f.get('format_note'):
                        sorted_formats.append(f)

                return sorted_formats[:15]  # Faqat 15 ta eng yaxshi format

            else:  # audio
                audio_formats = []
                for f in formats:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_formats.append(f)
                return audio_formats[:10]  # Faqat 10 ta audio format

    except Exception as e:
        print_with_delay(f"❌ Formatlarni olishda xatolik: {e}", 0.5)
        return []

def sizeof_fmt(num, suffix="B"):
    """Fayl hajmini o'qish qulay formatga o'tkazish"""
    if num is None:
        return "Noma'lum"
    for unit in ["", "K", "M", "G"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}T{suffix}"

def choose_format_interactive(url, mode="video"):
    """Foydalanuvchiga format tanlash imkoniyatini berish"""
    print_with_delay(f"\n📊 {mode.title()} formatlari yuklanmoqda...", 1)

    formats = get_available_formats(url, mode)

    if not formats:
        print_with_delay("❌ Formatlar topilmadi. Avtomatik tanlov qo'llaniladi.", 0.5)
        return 'best' if mode == 'video' else 'bestaudio'

    print(f"\n🎮 Mavjud {mode} formatlari:")
    print("=" * 80)

    for i, fmt in enumerate(formats):
        size = fmt.get('filesize') or fmt.get('filesize_approx')
        size_str = sizeof_fmt(size)
        quality = fmt.get('format_note', 'Noma\'lum')
        ext = fmt.get('ext', 'unknown')
        fps = fmt.get('fps', '')
        fps_str = f", {fps}fps" if fps else ""

        print(f"[{i+1}] {quality:8} | {size_str:8} | {ext:6} {fps_str}")

    print(f"[{len(formats)+1}] ✅ Avtomatik tanlov (eng yaxshi sifat)")
    print(f"[{len(formats)+2}] ⚡ Tez yuklash (720p)")
    print(f"[{len(formats)+3}] 📱 Mobil format (480p)")

    while True:
        try:
            choice = input(f"\n👉 Format raqamini tanlang (1-{len(formats)+3}): ").strip()

            if not choice:
                print_with_delay("⚠️  Avtomatik tanlov qo'llaniladi", 0.5)
                return 'best' if mode == 'video' else 'bestaudio'

            choice = int(choice)

            if 1 <= choice <= len(formats):
                selected_format = formats[choice-1]
                format_id = selected_format['format_id']
                quality = selected_format.get('format_note', 'tanlangan')
                print_with_delay(f"✅ {quality} sifat tanlandi!", 0.5)
                return format_id

            elif choice == len(formats) + 1:
                print_with_delay("🎯 Eng yaxshi sifat avtomatik tanlandi!", 0.5)
                return 'best' if mode == 'video' else 'bestaudio'

            elif choice == len(formats) + 2:
                print_with_delay("⚡ Tez yuklash (720p) tanlandi!", 0.5)
                return 'bestvideo[height<=720]+bestaudio/best[height<=720]'

            elif choice == len(formats) + 3:
                print_with_delay("📱 Mobil format (480p) tanlandi!", 0.5)
                return 'bestvideo[height<=480]+bestaudio/best[height<=480]'

            else:
                print("❌ Noto'g'ri raqam! Qaytadan urinib ko'ring.")

        except ValueError:
            print("❌ Faqat raqam kiriting!")
        except KeyboardInterrupt:
            print_with_delay("\n⚠️  Avtomatik tanlov qo'llaniladi", 0.5)
            return 'best' if mode == 'video' else 'bestaudio'

def download_media(url: str, code: str, mode="video", DOWNLOADS_DIR=None):
    """Media yuklab olish"""
    # Format tanlash
    format_choice = input("\n🎛️  Formatni o'zingiz tanlamoqchimisiz? [h]a/[y]oq: ").lower().strip()

    if format_choice.startswith('h'):
        format_id = choose_format_interactive(url, mode)
    else:
        format_id = 'best' if mode == 'video' else 'bestaudio'
        print_with_delay("✅ Eng yaxshi sifat avtomatik tanlandi!", 0.5)

    ext = "mp3" if mode == "audio" else "mp4"
    filename = f"{code}.%(ext)s"

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOADS_DIR, filename),
        'format': format_id,
        'quiet': False,
        'no_warnings': False,
    }

    if mode == "audio":
        # FFmpeg bo'lmasa, konvertatsiyasiz ishlash
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        except:
            print_with_delay("⚠️  FFmpeg topilmadi. Audio original formatda saqlanadi.", 0.5)
            ext = "m4a"

    try:
        print_with_delay("\n📥 Yuklab olinmoqda...", 1)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print_with_delay(f"\n✅ Muvaffaqiyatli yuklab olindi: {code}.{ext}", 1)
        print_with_delay(f"📁 Saqlangan joy: {DOWNLOADS_DIR}", 0.5)

        # Muvaffaqiyatli animatsiya
        for emoji in ["🎉", "✨", "🔥"]:
            print_with_delay(emoji, 0.3)

    except Exception as e:
        print_with_delay(f"❌ Yuklab olishda xatolik: {e}", 0.5)

def main():
    """Asosiy dastur"""
    if not check_and_install_requirements():
        print_with_delay("\n⚠️  FFmpeg o'rnatilmadi, lekin dastur ishlaydi", 1)

    DOWNLOADS_DIR = setup_directories()
    show_banner()

    try:
        while True:
            print_with_delay("\n" + "="*60, 0.3)
            url = input("\n🔗 Video URL manzilini kiriting (yoki 'q' chiqish): ").strip()
            if url.lower() == "q":
                print_with_delay("\n👋 Xayr! Dastur tugadi.", 1)
                break

            mode = input("📀 [v]ideo yoki [a]udio (mp3) sifatida yuklab olish? ").lower().strip()
            if mode.startswith("a"):
                mode = "audio"
                print_with_delay("🎵 Audio rejimi tanlandi", 0.5)
            else:
                mode = "video"
                print_with_delay("🎥 Video rejimi tanlandi", 0.5)

            code = input("📂 Fayl nomi (kod): ").strip()
            print_with_delay(f"📝 Fayl nomi: {code}", 0.3)

            download_media(url, code, mode, DOWNLOADS_DIR)

    except KeyboardInterrupt:
        print_with_delay("\n\n👋 Xayr! Siz Ctrl+C bosdingiz, dastur to'xtadi.", 1)
    except Exception as e:
        print_with_delay(f"\n❌ Kutilmagan xatolik: {e}", 0.5)

if __name__ == "__main__":
    main()