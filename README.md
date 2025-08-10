# 📖 User Guide - Social Media Automation V2

## 🚀 Panduan Lengkap Penggunaan Aplikasi Web

### 📋 Daftar Isi
1. [Instalasi dan Setup](#instalasi-dan-setup)
2. [Login dan Dashboard](#login-dan-dashboard)
3. [Mengelola Akun Social Media](#mengelola-akun-social-media)
4. [Guest Posting Setup](#guest-posting-setup)
5. [Membuat dan Mengelola Konten](#membuat-dan-mengelola-konten)
6. [Posting Otomatis](#posting-otomatis)
7. [Automation dan Scheduling](#automation-dan-scheduling)
8. [Settings dan Konfigurasi](#settings-dan-konfigurasi)
9. [Tips dan Best Practices](#tips-dan-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Instalasi dan Setup

### 1. **Persiapan Sistem**
```bash
# Pastikan Python 3.8+ terinstall
python --version

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env
# Edit .env dengan API keys Anda
```

### 2. **Menjalankan Aplikasi**
```bash
# Windows
run_windows.bat

# Manual
python app_complete.py
```

### 3. **Akses Web Interface**
- Buka browser dan kunjungi: `http://localhost:5000`
- Aplikasi akan otomatis redirect ke dashboard

---

## 🏠 Login dan Dashboard

### **Dashboard Overview**
Dashboard adalah halaman utama yang menampilkan:

#### **📊 Statistics Cards**
- **Total Accounts**: Jumlah akun social media yang terhubung
- **Total Posts**: Jumlah total postingan yang dibuat
- **Success Rate**: Persentase keberhasilan posting
- **Pending Posts**: Postingan yang menunggu dijadwalkan

#### **📈 Charts dan Analytics**
- **Posts Chart**: Grafik postingan dalam 7 hari terakhir
- **Platform Distribution**: Distribusi postingan per platform
- **Success Rate Trend**: Tren tingkat keberhasilan

#### **📝 Recent Posts**
- Daftar 10 postingan terbaru
- Status setiap postingan (Published, Failed, Scheduled)
- Quick actions (View, Edit, Retry)

#### **⚡ Quick Actions**
- **Scrape WordPress**: Ambil konten dari WordPress sites
- **Process Posts**: Proses postingan yang pending
- **Refresh Dashboard**: Update data real-time

---

## 👥 Mengelola Akun Social Media

### **1. Menambah Akun Baru**

#### **Langkah-langkah:**
1. Klik **"Accounts"** di sidebar
2. Klik tombol **"Add Account"**
3. Isi form dengan informasi:
   - **Platform**: Facebook, Instagram, Twitter, LinkedIn
   - **Account Name**: Nama untuk identifikasi (contoh: "My Business FB")
   - **Username/Email**: Username atau email login
   - **Password**: Password akun
   - **Notes**: Catatan tambahan (opsional)

#### **Platform yang Didukung:**

##### **🔵 Facebook**
- **Login**: Email atau username
- **Features**: Post text, images, videos, stories
- **Auto-detection**: Page vs Personal profile

##### **📷 Instagram**
- **Login**: Username atau email
- **Features**: Post photos, videos, stories, reels
- **Media Support**: JPG, PNG, MP4
- **Auto-hashtags**: Otomatis generate hashtags

##### **🐦 Twitter**
- **Login**: Username atau email
- **Features**: Tweet text, images, threads
- **Character Limit**: Auto-split untuk tweet panjang

##### **💼 LinkedIn**
- **Login**: Email
- **Features**: Post text, images, articles
- **Professional Tone**: Auto-optimize untuk audience profesional

### **2. Testing Koneksi Akun**
- Klik tombol **"Test"** pada akun
- Sistem akan verifikasi login credentials
- Status akan berubah menjadi "Active" jika berhasil

### **3. Mengelola Status Akun**
- **Active**: Akun siap digunakan
- **Needs Attention**: Perlu reconnect
- **Disconnected**: Akun tidak aktif

### **4. Reconnect Akun**
- Jika akun bermasalah, klik **"Reconnect"**
- Sistem akan mencoba login ulang
- Update password jika diperlukan

---

## 🌐 Guest Posting Setup

### **1. Menambah Guest Posting Site**

#### **Langkah-langkah:**
1. Klik **"Guest Posting"** di sidebar
2. Klik **"Add New Site"**
3. Isi informasi site:
   - **Site Name**: Nama website (contoh: "Tech Blog")
   - **Website URL**: URL utama website
   - **Login URL**: URL halaman login admin
   - **Username**: Username admin
   - **Password**: Password admin
   - **CMS Type**: WordPress, Blogger, Medium, Custom

#### **CMS yang Didukung:**

##### **📝 WordPress**
- **Auto-detection**: Otomatis detect WordPress admin
- **Features**: Post articles, set categories, tags
- **Media Upload**: Support gambar dan video
- **SEO**: Auto-fill meta description

##### **📰 Blogger**
- **Google Integration**: Login dengan Google account
- **Features**: Publish posts, set labels
- **Template Support**: Maintain blog styling

##### **✍️ Medium**
- **Publication Support**: Post ke publication
- **Features**: Rich text formatting, tags
- **Auto-import**: Import dari draft

##### **🔧 Custom CMS**
- **XPath Selectors**: Flexible element detection
- **Form Mapping**: Auto-map form fields
- **Adaptive**: Learn dari user interaction

### **2. Testing Site Connection**
- Klik **"Test Connection"** pada site
- Sistem akan verifikasi login dan akses admin
- Check posting permissions

### **3. Site Management**
- **Edit**: Update credentials atau settings
- **Disable**: Temporary disable site
- **Delete**: Remove site permanently

---

## 📝 Membuat dan Mengelola Konten

### **1. Content Sources**

#### **📰 WordPress Scraping**
1. Klik **"Content"** di sidebar
2. Klik **"Scrape WordPress"**
3. Masukkan URL WordPress site
4. Pilih kategori atau tag yang ingin di-scrape
5. Sistem akan otomatis import artikel

#### **✍️ Manual Content Creation**
1. Klik **"Create New Content"**
2. Isi form:
   - **Title**: Judul konten
   - **Content**: Isi konten (support Markdown)
   - **Tags**: Tags untuk kategorisasi
   - **Category**: Kategori konten
   - **Source URL**: URL sumber (jika ada)

#### **🤖 AI Content Generation**
1. Klik **"Generate with AI"**
2. Isi prompt:
   - **Topic**: Topik yang ingin dibahas
   - **Tone**: Professional, Casual, Friendly, Formal
   - **Length**: Short (50-100 words), Medium (100-250), Long (250-500)
   - **Platform**: Optimize untuk platform tertentu
3. Klik **"Generate"**
4. Edit hasil sesuai kebutuhan

### **2. Content Management**

#### **📋 Content Library**
- **Filter**: Filter berdasarkan status, kategori, tags
- **Search**: Cari konten berdasarkan judul atau isi
- **Bulk Actions**: Select multiple content untuk bulk operations

#### **✏️ Content Editing**
- **Rich Text Editor**: WYSIWYG editor dengan formatting
- **Markdown Support**: Write dalam Markdown syntax
- **Preview**: Preview hasil sebelum publish
- **Version History**: Track perubahan konten

#### **🔄 Content Improvement**
1. Select konten yang ingin diperbaiki
2. Klik **"Improve with AI"**
3. Pilih jenis improvement:
   - **Grammar & Spelling**: Perbaiki grammar
   - **SEO Optimization**: Optimize untuk SEO
   - **Readability**: Improve readability score
   - **Engagement**: Increase engagement potential
4. Review dan apply changes

### **3. Content Status**
- **Draft**: Konten belum siap publish
- **Ready**: Konten siap untuk posting
- **Published**: Konten sudah di-post
- **Archived**: Konten lama yang di-archive

---

## 📤 Posting Otomatis

### **1. Creating Posts**

#### **📝 Manual Post Creation**
1. Klik **"Posts"** di sidebar
2. Klik **"Create New Post"**
3. Isi form posting:
   - **Content Source**: Pilih dari content library atau buat baru
   - **Title**: Judul post (auto-fill dari content)
   - **Content**: Isi post (editable)
   - **Platform**: Pilih platform target
   - **Account**: Pilih akun yang akan digunakan
   - **Schedule**: Set waktu posting atau post immediately

#### **🎯 Platform-Specific Optimization**
- **Facebook**: Auto-add engaging questions, optimal image size
- **Instagram**: Auto-generate hashtags, square image format
- **Twitter**: Auto-split long content, add trending hashtags
- **LinkedIn**: Professional tone, industry-relevant tags

#### **📅 Scheduling Options**
- **Post Now**: Langsung publish
- **Schedule**: Set tanggal dan waktu spesifik
- **Recurring**: Set posting berulang (daily, weekly, monthly)
- **Best Time**: AI-suggested optimal posting time

### **2. Bulk Posting**
1. Select multiple content dari library
2. Klik **"Bulk Create Posts"**
3. Pilih:
   - **Target Platforms**: Multiple platforms sekaligus
   - **Accounts**: Multiple accounts per platform
   - **Schedule**: Distribute posting dalam timeframe
4. Sistem akan create posts untuk semua kombinasi

### **3. Post Management**

#### **📊 Post Status Tracking**
- **Draft**: Post belum dijadwalkan
- **Scheduled**: Post dijadwalkan, menunggu waktu
- **Processing**: Post sedang diproses
- **Published**: Post berhasil dipublish
- **Failed**: Post gagal, perlu retry

#### **🔄 Failed Post Handling**
- **Auto-retry**: Sistem otomatis retry failed posts
- **Manual Retry**: Klik "Retry" pada failed post
- **Error Analysis**: Lihat detail error message
- **Account Check**: Verify account masih aktif

#### **📈 Post Analytics**
- **Engagement Metrics**: Likes, comments, shares
- **Reach**: Jumlah orang yang melihat
- **Click-through**: Jika ada link dalam post
- **Performance Comparison**: Compare across platforms

---

## ⚙️ Automation dan Scheduling

### **1. Automation Rules**

#### **🔄 Auto-posting Rules**
1. Klik **"Automation"** di sidebar
2. Klik **"Create New Rule"**
3. Setup rule:
   - **Trigger**: WordPress new post, RSS feed update, manual
   - **Content Source**: Specific category, tag, atau all
   - **Target Platforms**: Select platforms
   - **Accounts**: Select accounts per platform
   - **Schedule**: Immediate, delayed, atau recurring

#### **📋 Rule Examples**
- **Blog to Social**: Auto-post new blog articles ke semua platform
- **RSS to Instagram**: Auto-post RSS feed items ke Instagram
- **Content Recycling**: Re-post old popular content
- **Cross-posting**: Post dari satu platform ke platform lain

### **2. Scheduling System**

#### **📅 Schedule Types**
- **One-time**: Single post pada waktu tertentu
- **Recurring**: Daily, weekly, monthly posting
- **Smart Schedule**: AI-optimized posting times
- **Bulk Schedule**: Schedule multiple posts sekaligus

#### **⏰ Optimal Timing**
- **Platform Analytics**: Berdasarkan audience activity
- **Industry Best Practices**: Waktu optimal per industri
- **Custom Schedule**: Set manual berdasarkan preference
- **Time Zone Support**: Multi-timezone scheduling

### **3. Automation Monitoring**

#### **📊 Automation Dashboard**
- **Active Rules**: Rules yang sedang berjalan
- **Execution History**: History automation runs
- **Success Rate**: Tingkat keberhasilan automation
- **Error Logs**: Log errors untuk troubleshooting

#### **🔔 Notifications**
- **Email Alerts**: Notification via email
- **Browser Notifications**: Real-time browser alerts
- **Webhook Integration**: Send data ke external systems
- **Slack Integration**: Notifications ke Slack channel

---

## ⚙️ Settings dan Konfigurasi

### **1. General Settings**

#### **🌐 Application Settings**
- **Language**: Pilih bahasa interface
- **Timezone**: Set timezone untuk scheduling
- **Date Format**: Format tanggal display
- **Theme**: Light/Dark mode

#### **📝 Content Preferences**
- **Default Tone**: Tone default untuk AI generation
- **Default Length**: Panjang default konten
- **Auto Hashtags**: Enable/disable auto hashtag generation
- **Auto Optimization**: Platform-specific optimization

### **2. API Configuration**

#### **🤖 OpenAI Settings**
- **API Key**: Masukkan OpenAI API key
- **Model**: Pilih GPT model (3.5-turbo, GPT-4)
- **Max Tokens**: Limit tokens per request
- **Temperature**: Creativity level (0-2)

#### **🔑 Other API Keys**
- **Unsplash**: Untuk auto image sourcing
- **Pixabay**: Alternative image source
- **Webhook URL**: External notification endpoint

### **3. Security Settings**

#### **🛡️ Bot Security**
- **Rate Limiting**: Conservative, Moderate, Aggressive
- **User Agent Rotation**: Avoid detection
- **Proxy Support**: Use proxy untuk anonymity
- **Human Behavior**: Simulate human-like actions
- **Headless Mode**: Run browser in background

#### **🔒 Data Security**
- **Password Encryption**: Encrypt stored passwords
- **Data Retention**: How long to keep logs
- **Auto Backup**: Enable automatic backups
- **Export Data**: Export all data untuk backup

### **4. Performance Settings**

#### **⚡ Optimization**
- **Concurrent Posts**: Max simultaneous posts
- **Request Timeout**: Timeout untuk requests
- **Retry Attempts**: Max retry untuk failed operations
- **Cache Duration**: Cache settings untuk performance

#### **🐛 Debug Settings**
- **Log Level**: Error, Warning, Info, Debug
- **Debug Mode**: Enable detailed logging
- **Save Screenshots**: Save screenshots on errors
- **Verbose Logging**: Detailed operation logs

---

## 💡 Tips dan Best Practices

### **1. Account Management**
- **✅ DO**: Test accounts regularly untuk ensure connectivity
- **✅ DO**: Use strong, unique passwords
- **✅ DO**: Enable 2FA pada social media accounts
- **❌ DON'T**: Share account credentials
- **❌ DON'T**: Use same password untuk multiple accounts

### **2. Content Strategy**
- **✅ DO**: Create diverse content mix (text, images, videos)
- **✅ DO**: Use platform-specific optimization
- **✅ DO**: Schedule posts untuk optimal engagement times
- **❌ DON'T**: Post same content across all platforms
- **❌ DON'T**: Over-post atau spam followers

### **3. Automation Best Practices**
- **✅ DO**: Start dengan conservative rate limiting
- **✅ DO**: Monitor automation performance regularly
- **✅ DO**: Use human-like posting patterns
- **❌ DON'T**: Set too aggressive posting schedules
- **❌ DON'T**: Ignore failed post notifications

### **4. Security Recommendations**
- **✅ DO**: Regularly update passwords
- **✅ DO**: Use proxy jika posting volume tinggi
- **✅ DO**: Enable all security features
- **❌ DON'T**: Disable security measures untuk speed
- **❌ DON'T**: Ignore security warnings

### **5. Performance Optimization**
- **✅ DO**: Clear old logs regularly
- **✅ DO**: Backup data secara berkala
- **✅ DO**: Monitor system resources
- **❌ DON'T**: Run too many concurrent operations
- **❌ DON'T**: Ignore performance warnings

---

## 🔧 Troubleshooting

### **1. Common Issues**

#### **🔐 Login Problems**
**Problem**: Account login failed
**Solutions**:
- Verify username/password correct
- Check if account has 2FA enabled
- Try manual login di browser
- Update account credentials
- Check platform-specific requirements

#### **📝 Posting Failures**
**Problem**: Posts fail to publish
**Solutions**:
- Check account status (active/suspended)
- Verify content meets platform guidelines
- Check internet connection
- Review error messages dalam logs
- Try manual posting untuk test

#### **🤖 AI Generation Issues**
**Problem**: AI content generation fails
**Solutions**:
- Verify OpenAI API key valid
- Check API quota/billing
- Try simpler prompts
- Reduce max tokens setting
- Check internet connectivity

#### **⚡ Performance Issues**
**Problem**: Application runs slowly
**Solutions**:
- Clear browser cache
- Restart application
- Clear old logs
- Reduce concurrent operations
- Check system resources

### **2. Error Messages**

#### **"Account Connection Failed"**
- **Cause**: Invalid credentials atau account suspended
- **Solution**: Update credentials, check account status

#### **"Rate Limit Exceeded"**
- **Cause**: Too many requests dalam short time
- **Solution**: Reduce posting frequency, enable rate limiting

#### **"Content Violates Guidelines"**
- **Cause**: Content tidak sesuai platform guidelines
- **Solution**: Review dan edit content, check platform policies

#### **"API Key Invalid"**
- **Cause**: OpenAI API key salah atau expired
- **Solution**: Update API key dalam settings

### **3. Getting Help**

#### **📋 Logs dan Debugging**
1. Enable debug mode dalam settings
2. Check logs untuk detailed error messages
3. Save screenshots jika ada visual issues
4. Export logs untuk analysis

#### **🔄 Reset Options**
- **Reset Settings**: Reset ke default settings
- **Clear Cache**: Clear application cache
- **Reset Database**: Complete application reset (WARNING: deletes all data)

#### **📞 Support Resources**
- Check USER_GUIDE.md untuk detailed instructions
- Review TROUBLESHOOTING.md untuk common issues
- Check application logs untuk error details
- Export data untuk backup before major changes

---

## 🎯 Advanced Features

### **1. Custom XPath Selectors**
Untuk guest posting sites yang tidak standard:
- Inspect element untuk find selectors
- Test selectors dalam browser console
- Add custom selectors dalam site configuration

### **2. Webhook Integration**
Setup webhooks untuk external notifications:
- Configure webhook URL dalam settings
- Set notification triggers
- Test webhook delivery
- Monitor webhook logs

### **3. API Integration**
Integrate dengan external systems:
- Use REST API endpoints
- Authenticate dengan API keys
- Monitor API usage
- Handle rate limiting

### **4. Bulk Operations**
Efficient management untuk large datasets:
- Bulk import content dari CSV
- Bulk schedule posts
- Bulk update account settings
- Bulk export data

---

## 📊 Analytics dan Reporting

### **1. Performance Metrics**
- **Posting Success Rate**: Percentage successful posts
- **Platform Performance**: Compare performance across platforms
- **Content Engagement**: Track likes, shares, comments
- **Automation Efficiency**: Monitor automation performance

### **2. Custom Reports**
- **Daily Reports**: Daily posting summary
- **Weekly Analytics**: Weekly performance overview
- **Monthly Trends**: Long-term trend analysis
- **Custom Date Ranges**: Flexible reporting periods

### **3. Data Export**
- **CSV Export**: Export data untuk external analysis
- **JSON Export**: Complete data backup
- **PDF Reports**: Formatted reports untuk presentation
- **API Access**: Programmatic data access

---

## 🔄 Maintenance dan Updates

### **1. Regular Maintenance**
- **Weekly**: Clear old logs, check account status
- **Monthly**: Update passwords, review automation rules
- **Quarterly**: Full data backup, performance review
- **Annually**: Security audit, major updates

### **2. Update Process**
- **Check Updates**: Use built-in update checker
- **Backup Data**: Always backup before updates
- **Test Updates**: Test dalam staging environment
- **Monitor**: Monitor application after updates

### **3. Data Management**
- **Regular Backups**: Schedule automatic backups
- **Data Cleanup**: Remove old, unnecessary data
- **Archive**: Archive old content dan posts
- **Migration**: Plan untuk data migration jika needed

---

## 🎉 Kesimpulan

Social Media Automation V2 adalah powerful tool untuk:
- **Automate** social media posting across multiple platforms
- **Generate** high-quality content dengan AI
- **Manage** multiple accounts efficiently
- **Schedule** posts untuk optimal engagement
- **Monitor** performance dengan detailed analytics

Dengan mengikuti panduan ini, Anda dapat:
- ✅ Setup aplikasi dengan benar
- ✅ Configure accounts dan automation rules
- ✅ Create dan manage content effectively
- ✅ Monitor dan optimize performance
- ✅ Troubleshoot common issues

**Happy Automating! 🚀**

---

*Untuk pertanyaan lebih lanjut atau support, silakan check dokumentasi teknis atau contact support team.*

