import telebot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    Message, CallbackQuery, ChatMemberUpdated,
    InputMediaPhoto
)
import time
import random
import re
import json
import os
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import hashlib
import string

# ========== تنظیمات ==========
BOT_TOKEN = "8793482183:AAEGUa7ZEURP26N34DzKvrudnndC3q7apBk"
ADMIN_IDS = [8680457924]
bot = telebot.TeleBot(BOT_TOKEN)

# ========== دیتابیس فوق‌پیشرفته ==========
class UltraDatabase:
    def __init__(self):
        # تنظیمات گروه‌ها با امکانات جدید
        self.groups = {}
        # اطلاعات کاربران
        self.users = defaultdict(lambda: {
            "warnings": {},
            "muted_until": 0,
            "messages": deque(maxlen=30),
            "captcha_attempts": 0,
            "level": 0,
            "xp": 0,
            "last_activity": 0,
            "join_date": 0,
            "reports": [],
            "warns": 0,
            "strikes": 0,
            "verified": False,
            "referred_by": None,
            "referral_count": 0,
            "achievements": [],
            "banned_until": 0,
            "restricted_until": 0,
        })
        # داده‌های کپچا
        self.captcha = {}
        # زمان ورود
        self.join_times = defaultdict(list)
        # لینک‌های مخرب
        self.blocked_links = set([
            "telegram.org", "t.me", "telegram.me", "telegra.ph",
            "bit.ly", "tinyurl.com", "goo.gl", "shorturl.at",
            "t.ly", "rb.gy", "cut.ly", "shorte.st", "clck.ru",
            "is.gd", "v.gd", "qr.ae", "ow.ly", "buff.ly",
            "tiny.cc", "to.ly", "url.xyz", "linktr.ee",
        ])
        # کلمات ممنوعه
        self.bad_words = set([
            "فحش", "فحاشی", "فحش‌نامه", "فحاشی", "فحش‌گونه",
            "کیر", "کون", "کس", "گه", "گوه", "خر", "الاغ",
            "حروم", "حرامزاده", "لعنت", "لعنت‌زاده",
            "جاکش", "جنده", "فاحشه", "تن فروش",
            "خایه", "خایمال", "مادرجنده", "پدرجنده",
        ])
        # کلمات تبلیغاتی
        self.ad_keywords = set([
            "خرید", "فروش", "قیمت", "تخفیف", "فروشگاه", "سفارش",
            "اینجا کلیک کنید", "ثبت نام", "عضویت", "دانلود", "لینک",
            "تبلیغات", "تبلیغ", "اسپانسر", "حامی", "همکاری",
            "کسب درآمد", "درآمد", "کارایی", "موفقیت", "ثروت",
            "ارز دیجیتال", "بیت‌کوین", "اتریوم", "تتر", "دوجی",
            "فارکس", "سهام", "بورس", "ترید", "معاملات",
        ])
        # تنظیمات پیش‌فرض با امکانات جدید
        self.default_settings = {
            # تنظیمات قبلی
            "welcome": "👋 به گروه خوش آمدید {user_name}! لطفاً قوانین را رعایت کنید.\n📌 از دستور /rules برای دیدن قوانین استفاده کنید.",
            "welcome_enabled": True,
            "welcome_photo": None,
            "captcha": True,
            "captcha_timeout": 60,
            "captcha_max_attempts": 3,
            "anti_spam": True,
            "spam_threshold": 5,
            "spam_action": "mute",
            "spam_duration": 300,
            "anti_raid": True,
            "raid_threshold": 5,
            "raid_action": "kick",
            "anti_mentions": True,
            "mention_limit": 3,
            "anti_caps": True,
            "caps_limit": 70,
            "anti_emoji": True,
            "emoji_limit": 5,
            "anti_newlines": True,
            "newline_limit": 5,
            "auto_delete": False,
            "auto_delete_seconds": 60,
            "log_channel": None,
            "warn_limit": 3,
            "warn_action": "mute",
            "warn_duration": 3600,
            "max_warn_reset": 86400,
            
            # تنظیمات جدید فوق‌پیشرفته
            "anti_link": True,
            "anti_link_action": "warn",  # warn, mute, kick, ban
            "anti_link_whitelist": [],  # دامنه‌های مجاز
            "anti_bad_words": True,
            "anti_bad_words_action": "mute",
            "anti_bad_words_duration": 600,
            "anti_advertising": True,
            "anti_advertising_action": "kick",
            "anti_forward": True,
            "anti_forward_action": "warn",
            "anti_forward_limit": 3,
            "anti_commands": True,
            "anti_commands_action": "warn",
            "anti_commands_list": ["/ban", "/kick", "/mute", "/warn", "/add", "/delete"],
            "anti_reply_spam": True,
            "anti_reply_spam_threshold": 3,
            "anti_reply_spam_action": "mute",
            "anti_reply_spam_duration": 300,
            "anti_voice_spam": True,
            "anti_voice_spam_threshold": 3,
            "anti_voice_spam_action": "warn",
            "anti_media_spam": True,
            "anti_media_spam_threshold": 5,
            "anti_media_spam_action": "mute",
            
            # قفل گروه
            "group_lock": False,
            "group_lock_mode": "admin_only",  # admin_only, restricted_only, verified_only
            
            # سطح‌بندی
            "leveling_system": True,
            "level_xp_multiplier": 1.0,
            "level_message": "🎉 {user_name} به سطح {level} رسید!",
            
            # قوانین
            "rules": "📋 قوانین گروه:\n1. احترام به یکدیگر\n2. بدون اسپم و تبلیغات\n3. رعایت ادب و اخلاق\n4. بدون ارسال محتوای نامناسب\n5. همراهی با مدیریت",
            
            # ضدربات
            "anti_bot": True,
            "anti_bot_action": "ban",
            
            # گزارش‌گیری خودکار
            "auto_report": True,
            "auto_report_channel": None,
            
            # محدودیت سن کاربر (بر اساس تاریخ عضویت)
            "min_account_age": 0,  # روز
            
            # تایید دو مرحله‌ای
            "two_factor_auth": False,
            
            # اعلان‌ها
            "notifications_enabled": True,
            "notification_channel": None,
        }
        
    def get_group(self, group_id):
        if group_id not in self.groups:
            self.groups[group_id] = self.default_settings.copy()
        return self.groups[group_id]
    
    def get_user(self, user_id):
        return self.users[user_id]
    
    # ===== مدیریت اخطار =====
    def add_warning(self, group_id, user_id, reason):
        user = self.get_user(user_id)
        if group_id not in user["warnings"]:
            user["warnings"][group_id] = []
        user["warnings"][group_id].append({
            "time": time.time(),
            "reason": reason
        })
        user["warns"] += 1
        settings = self.get_group(group_id)
        now = time.time()
        user["warnings"][group_id] = [
            w for w in user["warnings"][group_id]
            if now - w["time"] < settings.get("max_warn_reset", 86400)
        ]
        return len(user["warnings"][group_id])
    
    def clear_warnings(self, group_id, user_id):
        user = self.get_user(user_id)
        if group_id in user["warnings"]:
            user["warnings"][group_id] = []
            user["warns"] = 0
            return True
        return False
    
    def get_warnings(self, group_id, user_id):
        user = self.get_user(user_id)
        return user["warnings"].get(group_id, [])
    
    # ===== مدیریت میوت =====
    def set_mute(self, user_id, duration):
        self.users[user_id]["muted_until"] = int(time.time()) + duration
    
    def remove_mute(self, user_id):
        self.users[user_id]["muted_until"] = 0
    
    def is_muted(self, user_id):
        return self.users[user_id]["muted_until"] > int(time.time())
    
    def get_mute_remaining(self, user_id):
        return max(0, self.users[user_id]["muted_until"] - int(time.time()))
    
    # ===== مدیریت بن موقت =====
    def set_temp_ban(self, user_id, duration):
        self.users[user_id]["banned_until"] = int(time.time()) + duration
    
    def is_temp_banned(self, user_id):
        return self.users[user_id]["banned_until"] > int(time.time())
    
    # ===== مدیریت پیام‌ها =====
    def add_message(self, user_id):
        self.users[user_id]["messages"].append(time.time())
        # افزایش XP
        if len(self.users[user_id]["messages"]) % 5 == 0:
            self.add_xp(user_id, 1)
    
    def get_message_count(self, user_id, seconds):
        now = time.time()
        msgs = self.users[user_id]["messages"]
        return sum(1 for t in msgs if now - t <= seconds)
    
    # ===== مدیریت ورود =====
    def add_join(self, group_id):
        now = time.time()
        self.join_times[group_id].append(now)
        if len(self.join_times[group_id]) > 30:
            self.join_times[group_id] = self.join_times[group_id][-30:]
    
    def get_join_count(self, group_id, seconds):
        now = time.time()
        return sum(1 for t in self.join_times[group_id] if now - t <= seconds)
    
    # ===== مدیریت کپچا =====
    def save_captcha(self, user_id, group_id, answer):
        self.captcha[user_id] = {
            "answer": answer,
            "time": time.time(),
            "group": group_id,
            "attempts": 0
        }
    
    def get_captcha(self, user_id):
        return self.captcha.get(user_id)
    
    def delete_captcha(self, user_id):
        if user_id in self.captcha:
            del self.captcha[user_id]
    
    def increment_captcha_attempts(self, user_id):
        if user_id in self.captcha:
            self.captcha[user_id]["attempts"] += 1
            return self.captcha[user_id]["attempts"]
        return 0
    
    # ===== سیستم سطح‌بندی =====
    def add_xp(self, user_id, amount):
        user = self.get_user(user_id)
        user["xp"] += amount
        user["last_activity"] = time.time()
        
        # محاسبه سطح جدید
        new_level = int(user["xp"] ** 0.5)  # ریشه دوم برای رشد تدریجی
        if new_level > user["level"]:
            user["level"] = new_level
            return True
        return False
    
    def get_level(self, user_id):
        user = self.get_user(user_id)
        return user["level"]
    
    def get_xp(self, user_id):
        user = self.get_user(user_id)
        return user["xp"]
    
    # ===== تایید =====
    def verify_user(self, user_id):
        self.users[user_id]["verified"] = True
    
    def is_verified(self, user_id):
        return self.users[user_id]["verified"]
    
    # ===== مدیریت پیام‌های ریپورت =====
    def add_report(self, user_id, report):
        self.users[user_id]["reports"].append({
            "time": time.time(),
            "report": report
        })
    
    # ===== بکاپ =====
    def backup(self):
        data = {
            "groups": self.groups,
            "users": dict(self.users),
            "stats": self.stats if hasattr(self, 'stats') else {},
            "timestamp": time.time()
        }
        with open(f"backup_{int(time.time())}.json", "w") as f:
            json.dump(data, f, indent=2)
        return True

db = UltraDatabase()

# ========== ابزارهای کمکی ==========
def is_admin(user_id, chat_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

def is_bot_admin(user_id):
    return user_id in ADMIN_IDS

def get_user_mention(user):
    name = user.first_name
    if user.username:
        return f"@{user.username}"
    return f"<a href='tg://user?id={user.id}'>{name}</a>"

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds} ثانیه"
    elif seconds < 3600:
        return f"{seconds // 60} دقیقه"
    elif seconds < 86400:
        return f"{seconds // 3600} ساعت"
    else:
        return f"{seconds // 86400} روز"

def contains_bad_words(text):
    text = text.lower()
    for word in db.bad_words:
        if word in text:
            return True
    return False

def contains_ad_keywords(text):
    text = text.lower()
    for word in db.ad_keywords:
        if word in text:
            return True
    return False

def contains_link(text):
    url_pattern = r'(https?://[^\s]+)|(www\.[^\s]+)|(t\.me/[^\s]+)|(telegram\.me/[^\s]+)'
    return re.search(url_pattern, text) is not None

def extract_links(text):
    url_pattern = r'(https?://[^\s]+)|(www\.[^\s]+)|(t\.me/[^\s]+)|(telegram\.me/[^\s]+)'
    return re.findall(url_pattern, text)

def is_forwarded(message):
    return message.forward_from is not None or message.forward_from_chat is not None

# ========== کیبوردهای پیشرفته ==========
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚙️ تنظیمات پیشرفته", callback_data="settings"),
        InlineKeyboardButton("📊 آمار گروه", callback_data="stats"),
        InlineKeyboardButton("📋 قوانین", callback_data="rules"),
        InlineKeyboardButton("🏆 رنکینگ", callback_data="ranking"),
        InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh"),
        InlineKeyboardButton("🆘 راهنما", callback_data="help")
    )
    return keyboard

def settings_menu(group_id):
    settings = db.get_group(group_id)
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # تنظیمات اصلی
    keyboard.add(
        InlineKeyboardButton("⚡ تنظیمات پایه", callback_data=f"basic_settings_{group_id}"),
        InlineKeyboardButton("🛡️ تنظیمات ضد اسپم", callback_data=f"antispam_settings_{group_id}"),
        InlineKeyboardButton("🚫 تنظیمات محدودیت", callback_data=f"restriction_settings_{group_id}"),
        InlineKeyboardButton("🔐 تنظیمات امنیت", callback_data=f"security_settings_{group_id}"),
        InlineKeyboardButton("🎯 تنظیمات پیشرفته", callback_data=f"advanced_settings_{group_id}"),
        InlineKeyboardButton("📝 قوانین", callback_data=f"rules_settings_{group_id}")
    )
    keyboard.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_main"))
    return keyboard

def basic_settings_menu(group_id):
    settings = db.get_group(group_id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    welcome_status = "✅" if settings['welcome_enabled'] else "❌"
    captcha_status = "✅" if settings['captcha'] else "❌"
    auto_delete_status = "✅" if settings['auto_delete'] else "❌"
    
    keyboard.add(
        InlineKeyboardButton(f"{welcome_status} پیام خوش‌آمدگویی", callback_data=f"toggle_welcome_{group_id}"),
        InlineKeyboardButton(f"{captcha_status} کپچا", callback_data=f"toggle_captcha_{group_id}"),
        InlineKeyboardButton(f"{auto_delete_status} حذف خودکار پیام‌ها", callback_data=f"toggle_autodelete_{group_id}"),
        InlineKeyboardButton("🔄 بازگشت", callback_data=f"back_settings_{group_id}")
    )
    return keyboard

def antispam_settings_menu(group_id):
    settings = db.get_group(group_id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    antispam_status = "✅" if settings['anti_spam'] else "❌"
    antiraid_status = "✅" if settings['anti_raid'] else "❌"
    
    keyboard.add(
        InlineKeyboardButton(f"{antispam_status} ضد اسپم (متن)", callback_data=f"toggle_antispam_{group_id}"),
        InlineKeyboardButton(f"{antiraid_status} ضد رید", callback_data=f"toggle_antiraid_{group_id}"),
        InlineKeyboardButton(f"📊 آستانه اسپم: {settings['spam_threshold']}", callback_data=f"set_spam_threshold_{group_id}"),
        InlineKeyboardButton(f"⏱️ مدت اسپم: {settings['spam_duration']}s", callback_data=f"set_spam_duration_{group_id}"),
        InlineKeyboardButton("🔄 بازگشت", callback_data=f"back_settings_{group_id}")
    )
    return keyboard

def restriction_settings_menu(group_id):
    settings = db.get_group(group_id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    antimentions_status = "✅" if settings['anti_mentions'] else "❌"
    anticaps_status = "✅" if settings['anti_caps'] else "❌"
    antiemoji_status = "✅" if settings['anti_emoji'] else "❌"
    antinl_status = "✅" if settings['anti_newlines'] else "❌"
    
    keyboard.add(
        InlineKeyboardButton(f"{antimentions_status} ضد منشن", callback_data=f"toggle_antimentions_{group_id}"),
        InlineKeyboardButton(f"{anticaps_status} ضد کپس", callback_data=f"toggle_anticaps_{group_id}"),
        InlineKeyboardButton(f"{antiemoji_status} ضد ایموجی", callback_data=f"toggle_antiemoji_{group_id}"),
        InlineKeyboardButton(f"{antinl_status} ضد خط جدید", callback_data=f"toggle_antinl_{group_id}"),
        InlineKeyboardButton("🔄 بازگشت", callback_data=f"back_settings_{group_id}")
    )
    return keyboard

def security_settings_menu(group_id):
    settings = db.get_group(group_id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    antibot_status = "✅" if settings['anti_bot'] else "❌"
    antilink_status = "✅" if settings['anti_link'] else "❌"
    antibad_status = "✅" if settings['anti_bad_words'] else "❌"
    antiad_status = "✅" if settings['anti_advertising'] else "❌"
    
    keyboard.add(
        InlineKeyboardButton(f"{antibot_status} ضد ربات", callback_data=f"toggle_antibot_{group_id}"),
        InlineKeyboardButton(f"{antilink_status} ضد لینک", callback_data=f"toggle_antilink_{group_id}"),
        InlineKeyboardButton(f"{antibad_status} ضد فحش", callback_data=f"toggle_antibad_{group_id}"),
        InlineKeyboardButton(f"{antiad_status} ضد تبلیغات", callback_data=f"toggle_antiad_{group_id}"),
        InlineKeyboardButton("🔄 بازگشت", callback_data=f"back_settings_{group_id}")
    )
    return keyboard

def advanced_settings_menu(group_id):
    settings = db.get_group(group_id)
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    group_lock_status = "🔒" if settings['group_lock'] else "🔓"
    level_status = "✅" if settings['leveling_system'] else "❌"
    report_status = "✅" if settings['auto_report'] else "❌"
    
    keyboard.add(
        InlineKeyboardButton(f"{group_lock_status} قفل گروه", callback_data=f"toggle_grouplock_{group_id}"),
        InlineKeyboardButton(f"{level_status} سیستم سطح‌بندی", callback_data=f"toggle_leveling_{group_id}"),
        InlineKeyboardButton(f"{report_status} گزارش خودکار", callback_data=f"toggle_autoreport_{group_id}"),
        InlineKeyboardButton(f"⚠️ اخطار تا جریمه: {settings['warn_limit']}", callback_data=f"set_warn_limit_{group_id}"),
        InlineKeyboardButton(f"🔊 کانال گزارش: {settings.get('log_channel', 'تنظیم نشده')}", callback_data=f"set_log_channel_{group_id}"),
        InlineKeyboardButton("🔄 بازگشت", callback_data=f"back_settings_{group_id}")
    )
    return keyboard

def rules_settings_menu(group_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📝 ویرایش قوانین", callback_data=f"edit_rules_{group_id}"),
        InlineKeyboardButton("📋 نمایش قوانین", callback_data=f"show_rules_{group_id}"),
        InlineKeyboardButton("🔄 بازگشت", callback_data=f"back_settings_{group_id}")
    )
    return keyboard

def back_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_main"))
    return keyboard

# ========== دستورات ==========
@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    text = f"""
✨ **ربات محافظ فوق‌پیشرفته Luffy Ultra** ✨
━━━━━━━━━━━━━━━━━━━━━━
👤 **کاربر:** {user.first_name}
🆔 **آیدی:** `{user.id}`
👑 **نقش:** {'👑 ادمین اصلی' if is_bot_admin(user.id) else '👤 کاربر'}
━━━━━━━━━━━━━━━━━━━━━━

🛡️ **قابلیت‌های فوق‌پیشرفته:**
• ضد اسپم، رید، منشن، کپس، ایموجی، خط جدید
• ضد لینک، فحش، تبلیغات، ربات، فوروارد
• سیستم کپچا هوشمند
• سیستم سطح‌بندی و امتیازدهی
• قفل گروه و محدودیت‌های پیشرفته
• گزارش‌گیری خودکار
• تایید دو مرحله‌ای
• و ده‌ها قابلیت دیگر!

📌 برای مدیریت گروه، بات را به گروه اضافه و ادمین کنید.
"""
    bot.reply_to(message, text, reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(commands=['settings'])
def settings_command(message):
    if not message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, "❌ این دستور فقط در گروه قابل استفاده است.")
        return
    group_id = message.chat.id
    if not is_admin(message.from_user.id, group_id) and not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "⛔ شما ادمین گروه نیستید!")
        return
    bot.reply_to(message, "⚙️ **تنظیمات پیشرفته گروه:**", reply_markup=settings_menu(group_id), parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if not message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, "❌ این دستور فقط در گروه قابل استفاده است.")
        return
    group_id = message.chat.id
    if not is_admin(message.from_user.id, group_id) and not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "⛔ شما ادمین گروه نیستید!")
        return
    try:
        members = bot.get_chat_members_count(group_id)
    except:
        members = "نامشخص"
    
    # آمار کامل
    total_warns = sum(len(user["warnings"].get(group_id, [])) for user in db.users.values())
    total_muted = sum(1 for user in db.users.values() if db.is_muted(user))
    
    text = f"""
📊 **آمار فوق‌پیشرفته گروه**
━━━━━━━━━━━━━━━━━━━━━━
👥 **تعداد اعضا:** {members}
📨 **پیام‌های کل:** {db.stats.get('total_messages', 0):,}
🚫 **اخراجی‌ها:** {db.stats.get('total_kicks', 0):,}
🔨 **بن‌ها:** {db.stats.get('total_bans', 0):,}
🔇 **میوت‌ها:** {db.stats.get('total_mutes', 0):,}
⚠️ **اخطارها:** {total_warns:,}
🔐 **کپچا موفق:** {db.stats.get('total_captcha_passed', 0):,}
❌ **کپچا ناموفق:** {db.stats.get('total_captcha_failed', 0):,}
🔇 **کاربران میوت:** {total_muted}
📊 **میانگین پیام در روز:** {db.stats.get('total_messages', 0) // max(1, (int(time.time()) - 0) // 86400)}
━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['rules'])
def rules_command(message):
    if not message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, "❌ این دستور فقط در گروه قابل استفاده است.")
        return
    group_id = message.chat.id
    settings = db.get_group(group_id)
    rules = settings.get('rules', 'قوانینی تنظیم نشده است.')
    bot.reply_to(message, f"📋 **قوانین گروه:**\n{rules}", parse_mode='HTML')

@bot.message_handler(commands=['ranking'])
def ranking_command(message):
    if not message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, "❌ این دستور فقط در گروه قابل استفاده است.")
        return
    group_id = message.chat.id
    
    # دریافت لیست کاربران گروه و رتبه‌بندی بر اساس سطح
    try:
        members = bot.get_chat_members(group_id)
        rankings = []
        for member in members:
            if not member.user.is_bot:
                user_id = member.user.id
                level = db.get_level(user_id)
                xp = db.get_xp(user_id)
                rankings.append((user_id, level, xp))
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        text = "🏆 **رنکینگ کاربران بر اساس سطح**\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, (user_id, level, xp) in enumerate(rankings[:10], 1):
            try:
                user = bot.get_chat_member(group_id, user_id).user
                name = user.first_name[:15]
                text += f"{i}. {name} - سطح {level} (XP: {xp})\n"
            except:
                continue
        
        if not text:
            text = "📭 هنوز داده‌ای برای نمایش وجود ندارد."
        
        bot.reply_to(message, text, parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ خطا در دریافت رنکینگ.")

@bot.message_handler(commands=['rank'])
def rank_command(message):
    user_id = message.from_user.id
    level = db.get_level(user_id)
    xp = db.get_xp(user_id)
    next_level_xp = (level + 1) ** 2
    progress = (xp / next_level_xp) * 100 if next_level_xp > 0 else 0
    
    text = f"""
🏆 **رتبه شما**
━━━━━━━━━━━━━━━━━━━━━━
👤 **کاربر:** {message.from_user.first_name}
📊 **سطح:** {level}
⭐ **امتیاز (XP):** {xp}
📈 **پیشرفت به سطح بعدی:** {progress:.1f}%
🔜 **XP مورد نیاز برای سطح بعدی:** {next_level_xp}
━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    text = """
📋 **راهنمای کامل ربات فوق‌پیشرفته**
━━━━━━━━━━━━━━━━━━━━━━
**دستورات عمومی:**
/start - منوی اصلی
/help - این راهنما
/rules - نمایش قوانین گروه
/rank - نمایش رتبه و سطح شما
/ranking - نمایش رنکینگ گروه

**دستورات مدیریت (فقط ادمین‌ها):**
/settings - تنظیمات پیشرفته
/stats - آمار کامل گروه
/ban [کاربر] - بن
/unban [کاربر] - آن‌بن
/kick [کاربر] - اخراج
/mute [کاربر] [مدت] - میوت
/unmute [کاربر] - رفع میوت
/warn [کاربر] [دلیل] - اخطار
/warnings [کاربر] - نمایش اخطارها
/resetwarnings [کاربر] - بازنشانی اخطارها
/purge (ریپلای) - پاک‌سازی
/pin (ریپلای) - پین
/unpin - برداشتن پین
/lock - قفل کردن گروه
/unlock - باز کردن قفل گروه
/backup - بکاپ‌گیری
/logs - نمایش لاگ‌های اخیر

**نکته:** در دستورات می‌توانید به جای آیدی، به پیام کاربر ریپلای کنید.
━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['lock', 'unlock'])
def lock_unlock_command(message):
    if not message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, "❌ این دستور فقط در گروه قابل استفاده است.")
        return
    group_id = message.chat.id
    if not is_admin(message.from_user.id, group_id) and not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "⛔ شما ادمین گروه نیستید!")
        return
    
    settings = db.get_group(group_id)
    if message.text.startswith('/lock'):
        settings['group_lock'] = True
        bot.reply_to(message, "🔒 گروه قفل شد. فقط ادمین‌ها می‌توانند پیام بفرستند.")
    else:
        settings['group_lock'] = False
        bot.reply_to(message, "🔓 قفل گروه باز شد.")

@bot.message_handler(commands=['backup'])
def backup_command(message):
    if not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "⛔ فقط ادمین اصلی می‌تواند بکاپ بگیرد.")
        return
    db.backup()
    bot.reply_to(message, "✅ بکاپ با موفقیت ذخیره شد.")

@bot.message_handler(commands=['logs'])
def logs_command(message):
    if not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "⛔ فقط ادمین اصلی می‌تواند لاگ ببیند.")
        return
    # نمایش لاگ‌های ساده از فایل
    try:
        with open("bot.log", "r") as f:
            logs = f.read().splitlines()[-20:]
        text = "📋 **لاگ‌های اخیر:**\n" + "\n".join(logs[-10:])
        bot.reply_to(message, text[:4000])
    except:
        bot.reply_to(message, "📭 فایل لاگ وجود ندارد.")

# ========== دستورات مدیریت ==========
@bot.message_handler(commands=['ban', 'unban', 'kick', 'mute', 'unmute', 'warn', 'warnings', 'resetwarnings', 'purge', 'pin', 'unpin'])
def admin_commands(message):
    if not message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, "❌ این دستور فقط در گروه قابل استفاده است.")
        return
    user_id = message.from_user.id
    group_id = message.chat.id
    if not is_admin(user_id, group_id) and not is_bot_admin(user_id):
        bot.reply_to(message, "⛔ شما ادمین گروه نیستید!")
        return

    command = message.text.split()[0].lower()
    args = message.text.split()[1:]

    def get_target_id():
        if args:
            target = args[0]
            if target.isdigit():
                return int(target)
        if message.reply_to_message:
            return message.reply_to_message.from_user.id
        return None

    if command == '/ban':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید (آیدی یا ریپلای).")
            return
        try:
            bot.ban_chat_member(group_id, target_id)
            db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
            bot.reply_to(message, f"✅ کاربر {target_id} بن شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/unban':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        try:
            bot.unban_chat_member(group_id, target_id)
            bot.reply_to(message, f"✅ کاربر {target_id} آن‌بن شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/kick':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        try:
            bot.ban_chat_member(group_id, target_id)
            bot.unban_chat_member(group_id, target_id)
            db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
            bot.reply_to(message, f"✅ کاربر {target_id} اخراج شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/mute':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        duration = int(args[1]) if len(args) > 1 else 300
        try:
            db.set_mute(target_id, duration)
            db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
            bot.reply_to(message, f"✅ کاربر {target_id} به مدت {format_duration(duration)} میوت شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/unmute':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        try:
            db.remove_mute(target_id)
            bot.reply_to(message, f"✅ میوت کاربر {target_id} برداشته شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/warn':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        reason = " ".join(args[1:]) if len(args) > 1 else "تخلف"
        try:
            count = db.add_warning(group_id, target_id, reason)
            settings = db.get_group(group_id)
            if count >= settings['warn_limit']:
                action = settings['warn_action']
                if action == "mute":
                    db.set_mute(target_id, settings['warn_duration'])
                    db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                    bot.reply_to(message, f"⚠️ کاربر {target_id} به دلیل {settings['warn_limit']} اخطار، {format_duration(settings['warn_duration'])} میوت شد.")
                elif action == "kick":
                    bot.ban_chat_member(group_id, target_id)
                    bot.unban_chat_member(group_id, target_id)
                    db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    bot.reply_to(message, f"⚠️ کاربر {target_id} به دلیل {settings['warn_limit']} اخطار، اخراج شد.")
                elif action == "ban":
                    bot.ban_chat_member(group_id, target_id)
                    db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                    bot.reply_to(message, f"⚠️ کاربر {target_id} به دلیل {settings['warn_limit']} اخطار، بن شد.")
                db.clear_warnings(group_id, target_id)
            else:
                bot.reply_to(message, f"⚠️ کاربر {target_id} اخطار {count}/{settings['warn_limit']} دریافت کرد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/warnings':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        try:
            warns = db.get_warnings(group_id, target_id)
            if warns:
                text = f"⚠️ **اخطارهای کاربر {target_id}:**\n"
                for i, w in enumerate(warns, 1):
                    text += f"{i}. {w['reason']} ({datetime.fromtimestamp(w['time']).strftime('%Y-%m-%d %H:%M')})\n"
                bot.reply_to(message, text, parse_mode='HTML')
            else:
                bot.reply_to(message, f"✅ کاربر {target_id} هیچ اخطاری ندارد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/resetwarnings':
        target_id = get_target_id()
        if not target_id:
            bot.reply_to(message, "⚠️ کاربر را مشخص کنید.")
            return
        try:
            if db.clear_warnings(group_id, target_id):
                bot.reply_to(message, f"✅ اخطارهای کاربر {target_id} بازنشانی شد.")
            else:
                bot.reply_to(message, f"❌ کاربر {target_id} اخطاری ندارد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/purge':
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ به پیامی ریپلای کنید تا از آن به بعد حذف شود.")
            return
        try:
            msg_id = message.reply_to_message.message_id
            count = 0
            while msg_id < message.message_id and count < 100:
                bot.delete_message(group_id, msg_id)
                msg_id += 1
                count += 1
            bot.reply_to(message, f"✅ {count} پیام حذف شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/pin':
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ به پیامی که می‌خواهید پین کنید ریپلای کنید.")
            return
        try:
            bot.pin_chat_message(group_id, message.reply_to_message.message_id)
            bot.reply_to(message, "📌 پیام پین شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

    elif command == '/unpin':
        try:
            bot.unpin_chat_message(group_id)
            bot.reply_to(message, "📌 پین برداشته شد.")
        except Exception as e:
            bot.reply_to(message, f"❌ خطا: {e}")

# ========== مدیریت اعضای جدید ==========
@bot.chat_member_handler()
def handle_new_member(chat_member_update: ChatMemberUpdated):
    chat = chat_member_update.chat
    if chat.type not in ['group', 'supergroup']:
        return
    group_id = chat.id
    new = chat_member_update.new_chat_member
    old = chat_member_update.old_chat_member
    
    if new.status == "member" and old.status in ["left", "kicked"]:
        user = new.user
        if user.is_bot:
            # ضد ربات
            settings = db.get_group(group_id)
            if settings['anti_bot']:
                try:
                    bot.ban_chat_member(group_id, user.id)
                    db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                    bot.send_message(group_id, f"🤖 ربات {user.first_name} شناسایی و بن شد.")
                except:
                    pass
            return
        
        user_id = user.id
        settings = db.get_group(group_id)
        db.add_join(group_id)
        
        # بررسی سن حساب کاربری
        if settings.get('min_account_age', 0) > 0:
            try:
                # محاسبه سن حساب (تخمینی با استفاده از تاریخ عضویت در تلگرام)
                # چون API تاریخ عضویت را نمی‌دهد، از روش جایگزین استفاده می‌کنیم
                # فقط برای کاربرانی که قبلاً در دیتابیس هستند
                pass
            except:
                pass
        
        # ضد رید
        if settings['anti_raid']:
            join_count = db.get_join_count(group_id, 10)
            if join_count >= settings['raid_threshold']:
                action = settings['raid_action']
                try:
                    if action == "kick":
                        bot.ban_chat_member(group_id, user_id)
                        bot.unban_chat_member(group_id, user_id)
                        db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    elif action == "ban":
                        bot.ban_chat_member(group_id, user_id)
                        db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                except:
                    pass
                return
        
        # کپچا
        if settings['captcha']:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            answer = num1 + num2
            db.save_captcha(user_id, group_id, answer)
            
            bot.send_message(
                group_id,
                f"🔐 {get_user_mention(user)}، لطفاً برای اثبات اینکه ربات نیستی، پاسخ این معادله را بفرست:\n\n{num1} + {num2} = ?\n\n⏳ شما {settings['captcha_timeout']} ثانیه فرصت دارید.",
                parse_mode='HTML'
            )
            
            def captcha_timeout():
                captcha_data = db.get_captcha(user_id)
                if captcha_data and captcha_data["group"] == group_id:
                    try:
                        bot.ban_chat_member(group_id, user_id)
                        bot.unban_chat_member(group_id, user_id)
                        db.stats['total_captcha_failed'] = db.stats.get('total_captcha_failed', 0) + 1
                        bot.send_message(group_id, f"⏰ {get_user_mention(user)} زمان کپچا تمام شد، اخراج شد.", parse_mode='HTML')
                    except:
                        pass
                    db.delete_captcha(user_id)
            
            threading.Timer(settings['captcha_timeout'], captcha_timeout).start()
        
        # پیام خوش‌آمدگویی
        if settings['welcome_enabled']:
            welcome_text = settings['welcome'].replace("{user_name}", user.first_name)
            bot.send_message(group_id, welcome_text, parse_mode='HTML')
        
        # ثبت تاریخ ورود
        db.users[user_id]["join_date"] = time.time()

# ========== پاسخ به کپچا ==========
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'] and message.text and message.text.lstrip('-').isdigit())
def captcha_answer(message):
    user_id = message.from_user.id
    group_id = message.chat.id
    captcha_data = db.get_captcha(user_id)
    
    if not captcha_data:
        return
    
    if captcha_data["group"] != group_id:
        return
    
    if int(message.text) == captcha_data["answer"]:
        db.delete_captcha(user_id)
        db.stats['total_captcha_passed'] = db.stats.get('total_captcha_passed', 0) + 1
        db.verify_user(user_id)
        bot.reply_to(message, "✅ کپچا صحیح بود! خوش آمدید.")
    else:
        attempts = db.increment_captcha_attempts(user_id)
        settings = db.get_group(group_id)
        max_attempts = settings.get('captcha_max_attempts', 3)
        
        if attempts >= max_attempts:
            try:
                bot.ban_chat_member(group_id, user_id)
                bot.unban_chat_member(group_id, user_id)
                db.stats['total_captcha_failed'] = db.stats.get('total_captcha_failed', 0) + 1
                bot.reply_to(message, f"❌ تعداد تلاش‌های شما بیش از حد مجاز بود، اخراج شدید.")
            except:
                pass
            db.delete_captcha(user_id)
        else:
            bot.reply_to(message, f"❌ پاسخ نادرست! تلاش {attempts}/{max_attempts}")

# ========== مدیریت پیام‌ها ==========
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'video_note'])
def handle_message(message):
    if not message.chat.type in ['group', 'supergroup']:
        return
    
    group_id = message.chat.id
    user = message.from_user
    user_id = user.id
    
    # نادیده گرفتن ادمین‌ها و بات
    if is_admin(user_id, group_id) or user.is_bot:
        return
    
    settings = db.get_group(group_id)
    
    # بررسی قفل گروه
    if settings['group_lock']:
        bot.delete_message(group_id, message.message_id)
        bot.send_message(group_id, f"🔒 {get_user_mention(user)} گروه قفل است! فقط ادمین‌ها می‌توانند پیام بفرستند.", parse_mode='HTML')
        return
    
    # بررسی میوت
    if db.is_muted(user_id):
        try:
            bot.delete_message(group_id, message.message_id)
            remaining = db.get_mute_remaining(user_id)
            bot.send_message(group_id, f"🔇 {get_user_mention(user)} شما میوت هستید! ({format_duration(remaining)} باقی مانده)", parse_mode='HTML')
        except:
            pass
        return
    
    # بررسی بن موقت
    if db.is_temp_banned(user_id):
        try:
            bot.delete_message(group_id, message.message_id)
            bot.send_message(group_id, f"🔨 {get_user_mention(user)} شما بن موقت هستید!", parse_mode='HTML')
        except:
            pass
        return
    
    # ضد اسپم
    if settings['anti_spam']:
        db.add_message(user_id)
        count = db.get_message_count(user_id, 1)
        if count >= settings['spam_threshold']:
            action = settings['spam_action']
            try:
                bot.delete_message(group_id, message.message_id)
                if action == "mute":
                    db.set_mute(user_id, settings['spam_duration'])
                    db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                    bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل اسپم به مدت {format_duration(settings['spam_duration'])} میوت شد.", parse_mode='HTML')
                elif action == "kick":
                    bot.ban_chat_member(group_id, user_id)
                    bot.unban_chat_member(group_id, user_id)
                    db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    bot.send_message(group_id, f"👢 {get_user_mention(user)} به دلیل اسپم اخراج شد.", parse_mode='HTML')
                elif action == "ban":
                    bot.ban_chat_member(group_id, user_id)
                    db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                    bot.send_message(group_id, f"🔨 {get_user_mention(user)} به دلیل اسپم بن شد.", parse_mode='HTML')
            except:
                pass
            return
    
    # ضد لینک
    if settings['anti_link'] and message.text:
        if contains_link(message.text):
            links = extract_links(message.text)
            # بررسی لیست سفید
            is_whitelisted = False
            for link in links:
                for whitelist in settings.get('anti_link_whitelist', []):
                    if whitelist in link:
                        is_whitelisted = True
                        break
            if not is_whitelisted:
                try:
                    bot.delete_message(group_id, message.message_id)
                    action = settings['anti_link_action']
                    if action == "warn":
                        count = db.add_warning(group_id, user_id, "ارسال لینک ممنوع")
                        bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً لینک نفرستید! (اخطار {count})", parse_mode='HTML')
                    elif action == "mute":
                        db.set_mute(user_id, 300)
                        db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                        bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل ارسال لینک میوت شد.", parse_mode='HTML')
                    elif action == "kick":
                        bot.ban_chat_member(group_id, user_id)
                        bot.unban_chat_member(group_id, user_id)
                        db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                        bot.send_message(group_id, f"👢 {get_user_mention(user)} به دلیل ارسال لینک اخراج شد.", parse_mode='HTML')
                    elif action == "ban":
                        bot.ban_chat_member(group_id, user_id)
                        db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                        bot.send_message(group_id, f"🔨 {get_user_mention(user)} به دلیل ارسال لینک بن شد.", parse_mode='HTML')
                except:
                    pass
                return
    
    # ضد فحش
    if settings['anti_bad_words'] and message.text:
        if contains_bad_words(message.text):
            try:
                bot.delete_message(group_id, message.message_id)
                action = settings['anti_bad_words_action']
                if action == "mute":
                    db.set_mute(user_id, settings.get('anti_bad_words_duration', 600))
                    db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                    bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل استفاده از الفاظ نامناسب میوت شد.", parse_mode='HTML')
                elif action == "kick":
                    bot.ban_chat_member(group_id, user_id)
                    bot.unban_chat_member(group_id, user_id)
                    db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    bot.send_message(group_id, f"👢 {get_user_mention(user)} به دلیل فحش اخراج شد.", parse_mode='HTML')
                elif action == "ban":
                    bot.ban_chat_member(group_id, user_id)
                    db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                    bot.send_message(group_id, f"🔨 {get_user_mention(user)} به دلیل فحش بن شد.", parse_mode='HTML')
                else:
                    count = db.add_warning(group_id, user_id, "فحش و الفاظ نامناسب")
                    bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً از الفاظ مناسب استفاده کنید! (اخطار {count})", parse_mode='HTML')
            except:
                pass
            return
    
    # ضد تبلیغات
    if settings['anti_advertising'] and message.text:
        if contains_ad_keywords(message.text):
            try:
                bot.delete_message(group_id, message.message_id)
                action = settings['anti_advertising_action']
                if action == "kick":
                    bot.ban_chat_member(group_id, user_id)
                    bot.unban_chat_member(group_id, user_id)
                    db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    bot.send_message(group_id, f"👢 {get_user_mention(user)} به دلیل تبلیغات اخراج شد.", parse_mode='HTML')
                elif action == "ban":
                    bot.ban_chat_member(group_id, user_id)
                    db.stats['total_bans'] = db.stats.get('total_bans', 0) + 1
                    bot.send_message(group_id, f"🔨 {get_user_mention(user)} به دلیل تبلیغات بن شد.", parse_mode='HTML')
                else:
                    count = db.add_warning(group_id, user_id, "تبلیغات")
                    bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً تبلیغ نفرستید! (اخطار {count})", parse_mode='HTML')
            except:
                pass
            return
    
    # ضد فوروارد
    if settings['anti_forward'] and is_forwarded(message):
        try:
            bot.delete_message(group_id, message.message_id)
            action = settings['anti_forward_action']
            if action == "warn":
                count = db.add_warning(group_id, user_id, "فوروارد پیام")
                bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً فوروارد نفرستید! (اخطار {count})", parse_mode='HTML')
            elif action == "mute":
                db.set_mute(user_id, 300)
                db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل فوروارد میوت شد.", parse_mode='HTML')
        except:
            pass
        return
    
    # ضد دستورات ادمین
    if settings['anti_commands'] and message.text:
        for cmd in settings['anti_commands_list']:
            if message.text.startswith(cmd):
                try:
                    bot.delete_message(group_id, message.message_id)
                    action = settings['anti_commands_action']
                    if action == "warn":
                        count = db.add_warning(group_id, user_id, f"استفاده از دستور {cmd}")
                        bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً از دستورات ادمین استفاده نکنید! (اخطار {count})", parse_mode='HTML')
                    elif action == "mute":
                        db.set_mute(user_id, 600)
                        db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                        bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل استفاده از دستورات ادمین میوت شد.", parse_mode='HTML')
                    break
                except:
                    pass
    
    # ضد منشن
    if settings['anti_mentions'] and message.text:
        mention_pattern = r'@\w+|tg://user\?id=\d+'
        mentions = len(re.findall(mention_pattern, message.text))
        if mentions > settings['mention_limit']:
            try:
                bot.delete_message(group_id, message.message_id)
                count = db.add_warning(group_id, user_id, f"منشن بیش از حد ({mentions} بار)")
                bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً منشن‌های زیاد نزنید! (اخطار {count})", parse_mode='HTML')
            except:
                pass
    
    # ضد کپس
    if settings['anti_caps'] and message.text:
        text = message.text
        letters = sum(1 for c in text if c.isalpha())
        if letters > 5:
            upper = sum(1 for c in text if c.isupper())
            ratio = (upper / letters) * 100 if letters > 0 else 0
            if ratio > settings['caps_limit']:
                try:
                    bot.delete_message(group_id, message.message_id)
                    count = db.add_warning(group_id, user_id, f"کپس بیش از حد ({ratio:.0f}%)")
                    bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً با حروف بزرگ پیام ندهید! (اخطار {count})", parse_mode='HTML')
                except:
                    pass
    
    # ضد ایموجی
    if settings['anti_emoji'] and message.text:
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002700-\U000027BF\U000024C2-\U0001F251]'
        emojis = len(re.findall(emoji_pattern, message.text))
        if emojis > settings['emoji_limit']:
            try:
                bot.delete_message(group_id, message.message_id)
                count = db.add_warning(group_id, user_id, f"ایموجی بیش از حد ({emojis} بار)")
                bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً از ایموجی زیاد استفاده نکنید! (اخطار {count})", parse_mode='HTML')
            except:
                pass
    
    # ضد خط جدید
    if settings['anti_newlines'] and message.text:
        newlines = message.text.count('\n')
        if newlines > settings['newline_limit']:
            try:
                bot.delete_message(group_id, message.message_id)
                count = db.add_warning(group_id, user_id, f"خط جدید بیش از حد ({newlines} بار)")
                bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً از خطوط جدید زیاد استفاده نکنید! (اخطار {count})", parse_mode='HTML')
            except:
                pass
    
    # ضد اسپم ریپلای
    if settings['anti_reply_spam'] and message.reply_to_message:
        if db.get_message_count(user_id, 5) > settings['anti_reply_spam_threshold']:
            try:
                bot.delete_message(group_id, message.message_id)
                action = settings['anti_reply_spam_action']
                if action == "mute":
                    db.set_mute(user_id, settings.get('anti_reply_spam_duration', 300))
                    db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                    bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل اسپم ریپلای میوت شد.", parse_mode='HTML')
                elif action == "kick":
                    bot.ban_chat_member(group_id, user_id)
                    bot.unban_chat_member(group_id, user_id)
                    db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    bot.send_message(group_id, f"👢 {get_user_mention(user)} به دلیل اسپم ریپلای اخراج شد.", parse_mode='HTML')
            except:
                pass
    
    # ضد اسپم صوتی
    if settings['anti_voice_spam'] and message.voice:
        if db.get_message_count(user_id, 10) > settings['anti_voice_spam_threshold']:
            try:
                bot.delete_message(group_id, message.message_id)
                action = settings['anti_voice_spam_action']
                if action == "warn":
                    count = db.add_warning(group_id, user_id, "اسپم صوتی")
                    bot.send_message(group_id, f"⚠️ {get_user_mention(user)} لطفاً پیام صوتی زیاد نفرستید! (اخطار {count})", parse_mode='HTML')
                elif action == "mute":
                    db.set_mute(user_id, 600)
                    db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                    bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل اسپم صوتی میوت شد.", parse_mode='HTML')
            except:
                pass
    
    # ضد اسپم مدیا
    if settings['anti_media_spam'] and (message.photo or message.video or message.document):
        if db.get_message_count(user_id, 10) > settings['anti_media_spam_threshold']:
            try:
                bot.delete_message(group_id, message.message_id)
                action = settings['anti_media_spam_action']
                if action == "mute":
                    db.set_mute(user_id, 600)
                    db.stats['total_mutes'] = db.stats.get('total_mutes', 0) + 1
                    bot.send_message(group_id, f"🔇 {get_user_mention(user)} به دلیل اسپم مدیا میوت شد.", parse_mode='HTML')
                elif action == "kick":
                    bot.ban_chat_member(group_id, user_id)
                    bot.unban_chat_member(group_id, user_id)
                    db.stats['total_kicks'] = db.stats.get('total_kicks', 0) + 1
                    bot.send_message(group_id, f"👢 {get_user_mention(user)} به دلیل اسپم مدیا اخراج شد.", parse_mode='HTML')
            except:
                pass
    
    # سیستم سطح‌بندی
    if settings['leveling_system']:
        if db.add_xp(user_id, 1):
            level = db.get_level(user_id)
            level_message = settings['level_message'].replace("{user_name}", user.first_name).replace("{level}", str(level))
            bot.send_message(group_id, f"🎉 {get_user_mention(user)} به سطح {level} رسید!", parse_mode='HTML')
    
    # حذف خودکار
    if settings['auto_delete']:
        def delete_later():
            try:
                bot.delete_message(group_id, message.message_id)
            except:
                pass
        threading.Timer(settings['auto_delete_seconds'], delete_later).start()
    
    # گزارش خودکار
    if settings['auto_report'] and settings.get('auto_report_channel'):
        try:
            report_channel = settings['auto_report_channel']
            bot.send_message(report_channel, f"📨 پیام جدید از {get_user_mention(user)}\nگروه: {group_id}\nمتن: {message.text[:200] if message.text else 'مدیا'}")
        except:
            pass

# ========== مدیریت کال‌بک‌ها ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data
    group_id = chat_id if call.message.chat.type in ['group', 'supergroup'] else None
    
    # بازگشت به منوی اصلی
    if data == "back_main":
        bot.edit_message_text(
            "✨ **منوی اصلی ربات فوق‌پیشرفته**",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu(),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    # تنظیمات
    if data == "settings":
        if not group_id:
            bot.answer_callback_query(call.id, "❌ این بخش فقط در گروه قابل استفاده است.")
            return
        if not is_admin(user_id, group_id) and not is_bot_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین گروه نیستید!")
            return
        bot.edit_message_text(
            "⚙️ **تنظیمات فوق‌پیشرفته گروه:**\nبرای تغییر هر بخش، روی گزینه مورد نظر کلیک کنید.",
            chat_id,
            call.message.message_id,
            reply_markup=settings_menu(group_id),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    # زیرمنوهای تنظیمات
    if data.startswith("basic_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "⚙️ **تنظیمات پایه:**",
            chat_id,
            call.message.message_id,
            reply_markup=basic_settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("antispam_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "🛡️ **تنظیمات ضد اسپم:**",
            chat_id,
            call.message.message_id,
            reply_markup=antispam_settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("restriction_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "🚫 **تنظیمات محدودیت:**",
            chat_id,
            call.message.message_id,
            reply_markup=restriction_settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("security_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "🔐 **تنظیمات امنیت:**",
            chat_id,
            call.message.message_id,
            reply_markup=security_settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("advanced_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "🎯 **تنظیمات پیشرفته:**",
            chat_id,
            call.message.message_id,
            reply_markup=advanced_settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("rules_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "📝 **تنظیمات قوانین:**",
            chat_id,
            call.message.message_id,
            reply_markup=rules_settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("back_settings_"):
        gid = int(data.split("_")[2])
        bot.edit_message_text(
            "⚙️ **تنظیمات فوق‌پیشرفته گروه:**",
            chat_id,
            call.message.message_id,
            reply_markup=settings_menu(gid),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    # آمار
    if data == "stats":
        if not group_id:
            bot.answer_callback_query(call.id, "❌ این بخش فقط در گروه قابل استفاده است.")
            return
        if not is_admin(user_id, group_id) and not is_bot_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین گروه نیستید!")
            return
        try:
            members = bot.get_chat_members_count(group_id)
        except:
            members = "نامشخص"
        
        total_warns = sum(len(user["warnings"].get(group_id, [])) for user in db.users.values())
        total_muted = sum(1 for user in db.users.values() if db.is_muted(user))
        
        text = f"""
📊 **آمار فوق‌پیشرفته گروه**
━━━━━━━━━━━━━━━━━━━━━━
👥 **تعداد اعضا:** {members}
📨 **پیام‌های کل:** {db.stats.get('total_messages', 0):,}
🚫 **اخراجی‌ها:** {db.stats.get('total_kicks', 0):,}
🔨 **بن‌ها:** {db.stats.get('total_bans', 0):,}
🔇 **میوت‌ها:** {db.stats.get('total_mutes', 0):,}
⚠️ **اخطارها:** {total_warns:,}
🔐 **کپچا موفق:** {db.stats.get('total_captcha_passed', 0):,}
❌ **کپچا ناموفق:** {db.stats.get('total_captcha_failed', 0):,}
🔇 **کاربران میوت:** {total_muted}
━━━━━━━━━━━━━━━━━━━━━━
"""
        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    # قوانین
    if data == "rules":
        if not group_id:
            bot.answer_callback_query(call.id, "❌ این بخش فقط در گروه قابل استفاده است.")
            return
        settings = db.get_group(group_id)
        rules = settings.get('rules', 'قوانینی تنظیم نشده است.')
        bot.edit_message_text(
            f"📋 **قوانین گروه:**\n{rules}",
            chat_id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    # رنکینگ
    if data == "ranking":
        if not group_id:
            bot.answer_callback_query(call.id, "❌ این بخش فقط در گروه قابل استفاده است.")
            return
        try:
            members = bot.get_chat_members(group_id)
            rankings = []
            for member in members:
                if not member.user.is_bot:
                    uid = member.user.id
                    level = db.get_level(uid)
                    xp = db.get_xp(uid)
                    rankings.append((uid, level, xp))
            rankings.sort(key=lambda x: x[1], reverse=True)
            
            text = "🏆 **رنکینگ کاربران بر اساس سطح**\n━━━━━━━━━━━━━━━━━━━━━━\n"
            for i, (uid, level, xp) in enumerate(rankings[:10], 1):
                try:
                    user = bot.get_chat_member(group_id, uid).user
                    name = user.first_name[:15]
                    text += f"{i}. {name} - سطح {level} (XP: {xp})\n"
                except:
                    continue
            
            if not text or text == "🏆 **رنکینگ کاربران بر اساس سطح**\n━━━━━━━━━━━━━━━━━━━━━━\n":
                text = "📭 هنوز داده‌ای برای نمایش وجود ندارد."
            
            bot.edit_message_text(
                text,
                chat_id,
                call.message.message_id,
                reply_markup=back_button(),
                parse_mode='HTML'
            )
        except:
            bot.edit_message_text(
                "❌ خطا در دریافت رنکینگ.",
                chat_id,
                call.message.message_id,
                reply_markup=back_button(),
                parse_mode='HTML'
            )
        bot.answer_callback_query(call.id)
        return
    
    # بروزرسانی
    if data == "refresh":
        bot.edit_message_text(
            "🔄 بروزرسانی شد.",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu(),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "✅ بروزرسانی انجام شد.")
        return
    
    # راهنما
    if data == "help":
        text = """
📋 **راهنمای کامل ربات فوق‌پیشرفته**
━━━━━━━━━━━━━━━━━━━━━━
**دستورات عمومی:**
/start - منوی اصلی
/help - این راهنما
/rules - نمایش قوانین
/rank - نمایش رتبه شما
/ranking - رنکینگ گروه

**دستورات مدیریت:**
/settings - تنظیمات پیشرفته
/stats - آمار کامل
/ban, /unban, /kick, /mute, /unmute
/warn, /warnings, /resetwarnings
/purge, /pin, /unpin
/lock, /unlock
/backup, /logs

**نکته:** در دستورات می‌توانید به پیام کاربر ریپلای کنید.
━━━━━━━━━━━━━━━━━━━━━━
"""
        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            reply_markup=back_button(),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        return
    
    # ===== Toggle تنظیمات =====
    if data.startswith("toggle_"):
        if not group_id:
            bot.answer_callback_query(call.id, "❌ این بخش فقط در گروه قابل استفاده است.")
            return
        if not is_admin(user_id, group_id) and not is_bot_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین گروه نیستید!")
            return
        
        parts = data.split("_")
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "❌ خطا.")
            return
        
        toggle = parts[1]
        gid = int(parts[2]) if parts[2].isdigit() else group_id
        
        settings = db.get_group(gid)
        
        if toggle == "welcome":
            settings['welcome_enabled'] = not settings['welcome_enabled']
        elif toggle == "captcha":
            settings['captcha'] = not settings['captcha']
        elif toggle == "autodelete":
            settings['auto_delete'] = not settings['auto_delete']
        elif toggle == "antispam":
            settings['anti_spam'] = not settings['anti_spam']
        elif toggle == "antiraid":
            settings['anti_raid'] = not settings['anti_raid']
        elif toggle == "antimentions":
            settings['anti_mentions'] = not settings['anti_mentions']
        elif toggle == "anticaps":
            settings['anti_caps'] = not settings['anti_caps']
        elif toggle == "antiemoji":
            settings['anti_emoji'] = not settings['anti_emoji']
        elif toggle == "antinl":
            settings['anti_newlines'] = not settings['anti_newlines']
        elif toggle == "antibot":
            settings['anti_bot'] = not settings['anti_bot']
        elif toggle == "antilink":
            settings['anti_link'] = not settings['anti_link']
        elif toggle == "antibad":
            settings['anti_bad_words'] = not settings['anti_bad_words']
        elif toggle == "antiad":
            settings['anti_advertising'] = not settings['anti_advertising']
        elif toggle == "grouplock":
            settings['group_lock'] = not settings['group_lock']
        elif toggle == "leveling":
            settings['leveling_system'] = not settings['leveling_system']
        elif toggle == "autoreport":
            settings['auto_report'] = not settings['auto_report']
        else:
            bot.answer_callback_query(call.id, "❌ تنظیم نامعتبر.")
            return
        
        # به‌روزرسانی منو
        if toggle in ["welcome", "captcha", "autodelete"]:
            bot.edit_message_text(
                "⚙️ **تنظیمات پایه:**",
                chat_id,
                call.message.message_id,
                reply_markup=basic_settings_menu(gid),
                parse_mode='HTML'
            )
        elif toggle in ["antispam", "antiraid"]:
            bot.edit_message_text(
                "🛡️ **تنظیمات ضد اسپم:**",
                chat_id,
                call.message.message_id,
                reply_markup=antispam_settings_menu(gid),
                parse_mode='HTML'
            )
        elif toggle in ["antimentions", "anticaps", "antiemoji", "antinl"]:
            bot.edit_message_text(
                "🚫 **تنظیمات محدودیت:**",
                chat_id,
                call.message.message_id,
                reply_markup=restriction_settings_menu(gid),
                parse_mode='HTML'
            )
        elif toggle in ["antibot", "antilink", "antibad", "antiad"]:
            bot.edit_message_text(
                "🔐 **تنظیمات امنیت:**",
                chat_id,
                call.message.message_id,
                reply_markup=security_settings_menu(gid),
                parse_mode='HTML'
            )
        elif toggle in ["grouplock", "leveling", "autoreport"]:
            bot.edit_message_text(
                "🎯 **تنظیمات پیشرفته:**",
                chat_id,
                call.message.message_id,
                reply_markup=advanced_settings_menu(gid),
                parse_mode='HTML'
            )
        
        status = "فعال" if settings.get(toggle if toggle != "welcome" else "welcome_enabled") else "غیرفعال"
        bot.answer_callback_query(call.id, f"✅ {toggle} به {status} تغییر کرد.")
        return
    
    # نمایش قوانین
    if data.startswith("show_rules_"):
        gid = int(data.split("_")[2])
        settings = db.get_group(gid)
        rules = settings.get('rules', 'قوانینی تنظیم نشده است.')
        bot.send_message(chat_id, f"📋 **قوانین گروه:**\n{rules}", parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    # ویرایش قوانین
    if data.startswith("edit_rules_"):
        gid = int(data.split("_")[2])
        bot.send_message(chat_id, "📝 لطفاً قوانین جدید را به صورت متنی ارسال کنید.\nبرای لغو، /cancel را بزنید.")
        # ذخیره وضعیت انتظار برای ویرایش قوانین
        # (در یک محیط واقعی باید state مدیریت شود)
        bot.answer_callback_query(call.id)
        return
    
    # تنظیمات عددی (مقداردهی)
    if data.startswith("set_"):
        bot.answer_callback_query(call.id, "⚠️ این بخش در نسخه فعلی قابل تنظیم نیست.")

# ========== پاسخ به پیام‌های متنی ساده ==========
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.chat.type in ['group', 'supergroup']:
        if message.text and message.text.lower() in ["سلام", "درود", "hi", "hello", "سلامی", "علیک"]:
            bot.reply_to(message, f"✨ سلام {message.from_user.first_name} جان! به گروه خوش آمدی! 🛡️")
    else:
        if message.text:
            bot.reply_to(message, "👋 سلام! لطفاً من رو به گروه اضافه کنید تا بتونم محافظت کنم.")

# ========== اجرا ==========
if __name__ == "__main__":
    print("=" * 70)
    print("✨ ربات محافظ فوق‌پیشرفته Luffy Ultra نسخه 6.0.0 ✨")
    print("=" * 70)
    print(f"👥 ادمین‌ها: {ADMIN_IDS}")
    print("✅ ربات با موفقیت راه‌اندازی شد.")
    print("📌 برای شروع، بات را به گروه اضافه کنید و /start بزنید.")
    print("=" * 70)
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"❌ خطا: {e}")
            print("🔄 راه‌اندازی مجدد در 5 ثانیه...")
            time.sleep(5)
            continue