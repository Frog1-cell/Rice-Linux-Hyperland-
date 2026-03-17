#!/bin/bash

# === Настройки ===
STATE_FILE="$HOME/.wallpaper_state"

ROFI_DIR="$HOME/.config/rofi/themes"
ALAC_DIR="$HOME/.config/alacritty"
HYPR_DIR="$HOME/.config/hypr"
AX_DIR="$HOME/.config/Ax-Shell"
ZSH_DIR="$HOME/.config/zsh"


# Читаем состояние темы
STATE=$(cat "$STATE_FILE" 2>/dev/null || echo 0)

if [ "$STATE" = "1" ]; then
    # === переключаемся на Ми Фу ===

    swww img ~/Изображения/ми-фу.png \
        --transition-type outer \
        --transition-pos top-right \
        --transition-step 75 \
        --transition-duration 4 \
        --transition-fps 50 &
    sleep 3.5

    # Rofi
    ln -sf "$ROFI_DIR/hyperland_custom.rasi" "$ROFI_DIR/current.rasi"
    pkill -x rofi

    # Alacritty
    ln -sf "$ALAC_DIR/theme_dark.toml" "$ALAC_DIR/theme.toml"
    alacritty msg config-reload

    # Hyprland
    ln -sf "$HYPR_DIR/border_dark.conf" "$HYPR_DIR/border.conf"
    hyprctl reload

    # Ax-Shell
    ln -sfn "$AX_DIR/styles_1" "$AX_DIR/styles"
    fabric-cli exec ax-shell 'app.set_css()'

    # Zsh тема
    ln -sfn "$ZSH_DIR/themes/theme_mifu.zsh" "$ZSH_DIR/current_theme.zsh"

    echo 0 > "$STATE_FILE"

else
    # === переключаемся на Джуань ===

    swww img ~/Изображения/чжуань-фаньи.jpg \
        --transition-type grow \
        --transition-pos top-right \
        --transition-step 75 \
        --transition-duration 4 \
        --transition-fps 50 &
    sleep 4

    # Rofi
    ln -sf "$ROFI_DIR/hyperland_custom_2.rasi" "$ROFI_DIR/current.rasi"
    pkill -x rofi

    # Alacritty
    ln -sf "$ALAC_DIR/theme_light.toml" "$ALAC_DIR/theme.toml"
    alacritty msg config-reload

    # Hyprland
    ln -sf "$HYPR_DIR/border_light.conf" "$HYPR_DIR/border.conf"
    hyprctl reload

    # Ax-Shell
    ln -sfn "$AX_DIR/styles_2" "$AX_DIR/styles"
    fabric-cli exec ax-shell 'app.set_css()'

    # Zsh тема
    ln -sfn "$ZSH_DIR/themes/theme_zhuan.zsh" "$ZSH_DIR/current_theme.zsh"

    echo 1 > "$STATE_FILE"
fi
