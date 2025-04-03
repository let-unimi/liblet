ε = 'ε'
DIAMOND = '◇'
HASH = '♯'
FONT_NAME = 'Fira Code'
GV_FONT_NAME = FONT_NAME
GV_FONT_SIZE = '12'  # must be a string
CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family={"+".join(FONT_NAME.split())}&display=swap');

pre, code {{
  font-family: '{FONT_NAME}', monospace !important;
  font-variant-ligatures: contextual common-ligatures !important;
  line-height: 1 !important;
}}

table.liblet {{
  border-collapse: collapse !important;
  font-family: '{FONT_NAME}', monospace !important;
  font-variant-ligatures: contextual common-ligatures !important;
}}

table.liblet th,
table.liblet td {{
  border: 1px solid black !important;
  padding: 0.5em !important;
  text-align: left !important;
}}

table.liblet th {{
  font-weight: bold !important;
}}

table.liblet th pre,
table.liblet td pre {{
  margin: 0 !important;
  font-family: inherit !important;
  font-weight: inherit !important;
}}
"""
