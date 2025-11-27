#!/usr/bin/env python3
"""Fix escaped quotes in ocr_agent.py"""

with open('src/agents/ocr_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace escaped quotes
content = content.replace('\\"', '"')

with open('src/agents/ocr_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Fixed escaped quotes in ocr_agent.py')
