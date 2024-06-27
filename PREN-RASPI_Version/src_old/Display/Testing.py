import digitalio
import board
from PIL import Image
from adafruit_rgb_display import color565
import adafruit_rgb_display.ili9341 as ili9341

# Konfiguration für SPI und Display
cs_pin = digitalio.DigitalInOut(board.CE0)  # Chip Select
dc_pin = digitalio.DigitalInOut(board.D25)  # Data/Command
reset_pin = digitalio.DigitalInOut(board.D24)  # Reset Pin kann auch None sein, falls nicht verfügbar

# Erstelle eine SPI-Instanz
spi = board.SPI()

# Initialisiere das Display
display = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, width=240, height=320)  # Stelle die Größe nach deinem Display ein

# Erstelle ein neues Bild mit der Größe des Displays. Die Farbe 'red' füllt den Hintergrund.
# Verwende "RGB" für Farbdisplays und "1" für monochrome Displays.
image = Image.new('RGB', (display.width, display.height), 'red')

# Zeige das Bild auf dem Display an
display.image(image)
