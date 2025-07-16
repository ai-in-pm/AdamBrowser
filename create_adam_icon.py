"""
Create a proper icon file for Adam Browser
"""

import wx
from PIL import Image, ImageDraw
import io

def create_adam_icon():
    """Create a proper Adam robot icon"""
    
    # Create a high-resolution icon (256x256)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Scale factor for high resolution
    scale = size / 100
    
    # Robot body (main rectangle)
    body_x = int(20 * scale)
    body_y = int(35 * scale)
    body_w = int(60 * scale)
    body_h = int(50 * scale)
    body_radius = int(10 * scale)
    
    # Draw robot body with rounded corners
    draw.rounded_rectangle(
        [body_x, body_y, body_x + body_w, body_y + body_h],
        radius=body_radius,
        fill=(70, 130, 180, 255),  # Steel blue
        outline=(25, 25, 112, 255),  # Dark blue border
        width=int(3 * scale)
    )
    
    # Robot head (circle)
    head_x = int(50 * scale)
    head_y = int(25 * scale)
    head_radius = int(18 * scale)
    
    draw.ellipse(
        [head_x - head_radius, head_y - head_radius, 
         head_x + head_radius, head_y + head_radius],
        fill=(100, 149, 237, 255),  # Cornflower blue
        outline=(25, 25, 112, 255),
        width=int(2 * scale)
    )
    
    # Eyes (white circles with black pupils)
    left_eye_x = int(43 * scale)
    right_eye_x = int(57 * scale)
    eye_y = int(22 * scale)
    eye_radius = int(4 * scale)
    pupil_radius = int(2 * scale)
    
    # Left eye
    draw.ellipse(
        [left_eye_x - eye_radius, eye_y - eye_radius,
         left_eye_x + eye_radius, eye_y + eye_radius],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255)
    )
    draw.ellipse(
        [left_eye_x - pupil_radius, eye_y - pupil_radius,
         left_eye_x + pupil_radius, eye_y + pupil_radius],
        fill=(0, 0, 0, 255)
    )
    
    # Right eye
    draw.ellipse(
        [right_eye_x - eye_radius, eye_y - eye_radius,
         right_eye_x + eye_radius, eye_y + eye_radius],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255)
    )
    draw.ellipse(
        [right_eye_x - pupil_radius, eye_y - pupil_radius,
         right_eye_x + pupil_radius, eye_y + pupil_radius],
        fill=(0, 0, 0, 255)
    )
    
    # Smile (arc)
    smile_y = int(28 * scale)
    smile_width = int(10 * scale)
    draw.arc(
        [int(45 * scale), smile_y, int(55 * scale), smile_y + int(4 * scale)],
        start=0, end=180,
        fill=(0, 0, 0, 255),
        width=int(2 * scale)
    )
    
    # Arms (lines)
    arm_width = int(6 * scale)
    # Left arm
    draw.line(
        [int(20 * scale), int(45 * scale), int(8 * scale), int(38 * scale)],
        fill=(70, 130, 180, 255),
        width=arm_width
    )
    # Right arm
    draw.line(
        [int(80 * scale), int(45 * scale), int(92 * scale), int(38 * scale)],
        fill=(70, 130, 180, 255),
        width=arm_width
    )
    
    # Hands (small circles)
    hand_radius = int(3 * scale)
    draw.ellipse(
        [int(8 * scale) - hand_radius, int(38 * scale) - hand_radius,
         int(8 * scale) + hand_radius, int(38 * scale) + hand_radius],
        fill=(100, 149, 237, 255)
    )
    draw.ellipse(
        [int(92 * scale) - hand_radius, int(38 * scale) - hand_radius,
         int(92 * scale) + hand_radius, int(38 * scale) + hand_radius],
        fill=(100, 149, 237, 255)
    )
    
    # Legs (lines)
    leg_width = int(6 * scale)
    draw.line(
        [int(35 * scale), int(85 * scale), int(35 * scale), int(95 * scale)],
        fill=(70, 130, 180, 255),
        width=leg_width
    )
    draw.line(
        [int(65 * scale), int(85 * scale), int(65 * scale), int(95 * scale)],
        fill=(70, 130, 180, 255),
        width=leg_width
    )
    
    # Feet (ellipses)
    foot_w = int(10 * scale)
    foot_h = int(5 * scale)
    draw.ellipse(
        [int(30 * scale), int(93 * scale), int(30 * scale) + foot_w, int(93 * scale) + foot_h],
        fill=(25, 25, 112, 255)
    )
    draw.ellipse(
        [int(60 * scale), int(93 * scale), int(60 * scale) + foot_w, int(93 * scale) + foot_h],
        fill=(25, 25, 112, 255)
    )
    
    # Antenna (line)
    antenna_width = int(3 * scale)
    draw.line(
        [int(50 * scale), int(7 * scale), int(50 * scale), int(15 * scale)],
        fill=(255, 215, 0, 255),  # Gold
        width=antenna_width
    )
    
    # Antenna tip (red circle)
    tip_radius = int(3 * scale)
    draw.ellipse(
        [int(50 * scale) - tip_radius, int(7 * scale) - tip_radius,
         int(50 * scale) + tip_radius, int(7 * scale) + tip_radius],
        fill=(255, 0, 0, 255)
    )
    
    # Chest panel (rectangle)
    panel_x = int(35 * scale)
    panel_y = int(50 * scale)
    panel_w = int(30 * scale)
    panel_h = int(20 * scale)
    draw.rounded_rectangle(
        [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
        radius=int(3 * scale),
        fill=(200, 200, 200, 255),
        outline=(100, 100, 100, 255)
    )
    
    # Chest buttons (small colored circles)
    button_radius = int(2 * scale)
    # Green button
    draw.ellipse(
        [int(42 * scale) - button_radius, int(57 * scale) - button_radius,
         int(42 * scale) + button_radius, int(57 * scale) + button_radius],
        fill=(0, 255, 0, 255)
    )
    # Red button
    draw.ellipse(
        [int(58 * scale) - button_radius, int(57 * scale) - button_radius,
         int(58 * scale) + button_radius, int(57 * scale) + button_radius],
        fill=(255, 0, 0, 255)
    )
    # Blue button
    draw.ellipse(
        [int(50 * scale) - button_radius, int(63 * scale) - button_radius,
         int(50 * scale) + button_radius, int(63 * scale) + button_radius],
        fill=(0, 0, 255, 255)
    )
    
    return img

def save_icon_files():
    """Save icon in multiple formats and sizes"""
    
    # Create the main icon
    icon_img = create_adam_icon()
    
    # Save as PNG
    icon_img.save('adam_robot_icon.png', 'PNG')
    print("✅ Saved adam_robot_icon.png")
    
    # Create smaller sizes for different uses
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        resized = icon_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'adam_robot_icon_{size}.png', 'PNG')
        print(f"✅ Saved adam_robot_icon_{size}.png")
    
    # Create ICO file (Windows icon format)
    try:
        # Create multiple sizes for ICO
        ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        ico_images = []
        
        for size in ico_sizes:
            resized = icon_img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(resized)
        
        # Save as ICO
        ico_images[0].save('adam_robot_icon.ico', format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print("✅ Saved adam_robot_icon.ico")
        
    except Exception as e:
        print(f"⚠️ Could not create ICO file: {e}")
    
    print("\n🎉 All icon files created successfully!")
    return 'adam_robot_icon.png'

if __name__ == '__main__':
    print("🤖 Creating Adam Robot Icon...")
    print("=" * 40)
    
    try:
        icon_path = save_icon_files()
        print(f"\n✅ Main icon saved as: {icon_path}")
        print("\nYou can now use these icon files in the widget!")
        
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        print("Make sure PIL (Pillow) is installed: pip install Pillow")
