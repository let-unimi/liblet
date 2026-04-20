ε = 'ε'
DIAMOND = '◇'
HASH = '♯'
FONT_NAME = 'Fira Code'
GV_FONT_NAME = FONT_NAME
GV_FONT_SIZE = '12'  # must be a string
CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family={"+".join(FONT_NAME.split())}&display=swap');

pre, code {{
  font-family: '{FONT_NAME}', monospace;
  font-variant-ligatures: contextual common-ligatures;
  line-height: 1.2 !important;
}}

table.liblet {{
  border-collapse: collapse;
  font-family: '{FONT_NAME}', monospace;
}}

table.liblet tr {{
  background: white !important;
}}

table.liblet th,
table.liblet td {{
  border: 1px solid black;
  padding: 0.5em;
  text-align: left !important;
}}

table.liblet th pre,
table.liblet td pre {{
  margin: 0;
  background: none;
  font-family: inherit;
  font-weight: inherit;
  text-align: left;
}}
"""
