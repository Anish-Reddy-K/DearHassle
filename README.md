# Dear Hassle - AI-Powered Job Application Assistant 🤖✍️

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-orange?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/anishreddyk)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/mit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)

Dear Hassle is an AI-powered tool that helps streamline your job application process by generating tailored cover letters, follow-up emails, and LinkedIn messages. Built with OpenAI's GPT models, it analyzes job descriptions to create personalized application materials that highlight your relevant experience and qualifications.

## ✨ Features

- 📝 **Cover Letter Generation**: Creates customized cover letters based on job descriptions
- 📧 **Follow-up Email Templates**: Generates professional follow-up email templates
- 🔗 **LinkedIn Messages**: Crafts connection messages within LinkedIn's character limit
- 📄 **Resume Context**: Uses your resume to ensure relevant experience is highlighted
- 🎨 **Customizable Templates**: Allows you to define your own templates for all message types

## 🚀 Quick Setup

Open your terminal and follow the instructions below:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anish-Reddy-K/DearHassle.git
   cd DearHassle
   ```

2. **Create a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```
5. **Open in browser**
   - The app will automatically open in your default browser
   - If not, visit `http://localhost:8501`
   
6. **Set up your OpenAI API key**
   - Get your API key from [OpenAI](https://platform.openai.com/account/api-keys)
   - Enter your key in the sidebar

## 💡 Usage Tips

1. Upload your resume (PDF or TXT)
2. Configure your personal information in the sidebar
3. Customize message templates to match your style
4. Paste a job description and click "Generate Documents"
5. Edit and preview your documents before downloading

## 🛠️ Customization

### Personal Information
Configure your details in the sidebar:
- Full Name
- Location
- Phone Number
- Email Address
- LinkedIn URL
- Portfolio URL
- GitHub URL

### Message Templates
Customize templates using placeholders:
- `{company_name}` - Company name
- `{position_title}` - Job title
- `{hiring_manager_name}` - Hiring manager's name
- And more...

## 📝 Requirements

- Python 3.10 or higher
- OpenAI API key
- Required packages:
  - streamlit
  - openai
  - python-dotenv
  - reportlab
  - PyPDF2

## 🤝 Support

If you found this tool helpful in your job search, your support would mean a lot! It helps me continue building free tools that make a difference.

<a href="https://www.buymeacoffee.com/anishreddyk"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=anishreddyk&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>

## 📬 Contact

- **Creator**: Anish Reddy
- **Email**: anishreddy3456@gmail.com
- **LinkedIn**: [Connect with me](https://linkedin.com/in/anishreddyk)
- **Portfolio**: [Visit my portfolio](https://anishreddyk.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ by <a href="https://anishreddyk.com">Anish Reddy</a></p>
