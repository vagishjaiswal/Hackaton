#!/usr/bin/env python
"""Clean up emoji characters from examples_agent_usage.py"""

with open('examples_agent_usage.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all emojis with ASCII
replacements = [
    ('📜', '[HISTORY]'),
    ('📊', '[ANALYSIS]'),
    ('✓', '[OK]'),
    ('❌', '[ERROR]'),
    ('✨', '[DONE]'),
]

for emoji, replacement in replacements:
    content = content.replace(emoji, replacement)

with open('examples_agent_usage.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('All emojis replaced successfully')
