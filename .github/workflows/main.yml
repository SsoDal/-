name: Real-time Economic Assistant
on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:
jobs:
  run_job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 google-generativeai pytz
      - name: Run Script
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        # 파일이 있는지 먼저 확인하고 실행하도록 수정
        run: |
          ls -la
          python main.py
