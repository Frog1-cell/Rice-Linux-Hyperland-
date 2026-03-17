#!/bin/bash

STATE_FILE="$HOME/.config/theme/current_state"
ROFI_DIR="$HOME/.config/rofi/themes"
ALAC_DIR="$HOME/.config/alacritty"
HYPR_DIR="$HOME/.config/hypr"
AX_DIR="$HOME/.config/Ax-Shell"

THEME="$(cat $STATE_FILE 2>/dev/null || echo "mi_fu")"

# === ОБОИ ===
if [ "$THEME" = "mi_fu" ]; then
    swww img ~/Изображения/ми-фу.png &
else
    swww img ~/Изображения/чжуань-фаньи.jpg &
fi

# === ROFI ===
ln -sf "$ROFI_DIR/hyperland_custom_${THEME}.rasi" "$ROFI_DIR/current.rasi"

# === ALACRITTY ===
ln -sf "$ALAC_DIR/theme_${THEME}.toml" "$ALAC_DIR/theme.toml"
alacritty msg config-reload

# === HYPRLAND BORDER ===
ln -sf "$HYPR_DIR/border_${THEME}.conf" "$HYPR_DIR/border.conf"
hyprctl reload

# === AX-SHELL ===
if [ "$THEME" = "juan" ]; then
    mv "$AX_DIR/styles" "$AX_DIR/styles_tmp"
    mv "$AX_DIR/styles_2" "$AX_DIR/styles"
    mv "$AX_DIR/styles_tmp" "$AX_DIR/styles_2"
fi
fabric-cli exec ax-shell 'app.set_css()'
