#!/usr/bin/env sh

# Небольшая начальная задержка на всякий случай (можно убрать, если не нужна)
sleep 0.1

# Фиксированная папка для сохранения скриншотов
save_dir="$HOME/Изображения/Ax-Shell ⇢"
# Убеждаемся, что папка существует
mkdir -p "$save_dir"

# Формируем имя файла с датой
save_file=$(date +'%y%m%d_%Hh%Mm%Ss_screenshot.png')
full_path="$save_dir/$save_file"

# Параметр mockup (если передан)
mockup_mode="$2"

print_error() {
    cat <<EOF
    ./screenshot.sh <action> [mockup]
    ...valid actions are...
        p  : print selected screen
        s  : snip selected region
        w  : snip focused window
EOF
}

case $1 in
    p)
        hyprshot -z -s -m output -o "$save_dir" -f "$save_file"
        ;;
    s)
        hyprshot -z -s -m region -o "$save_dir" -f "$save_file"
        ;;
    w)
        hyprshot -s -m window -o "$save_dir" -f "$save_file"
        ;;
    *)
        print_error
        exit 1
        ;;
esac

# Если файл успешно создан
if [ -f "$full_path" ]; then
    # Копируем в буфер обмена, если не mockup
    if [ "$mockup_mode" != "mockup" ]; then
        if command -v wl-copy >/dev/null 2>&1; then
            wl-copy < "$full_path"
        elif command -v xclip >/dev/null 2>&1; then
            xclip -selection clipboard -t image/png < "$full_path"
        fi
    fi

    # Обработка mockup (если запрошено)
    if [ "$mockup_mode" = "mockup" ]; then
        temp_file="${full_path%.png}_temp.png"
        mockup_file="${full_path%.png}_mockup.png"
        mockup_success=true

        # Скругление углов и прозрачность
        if [ "$mockup_success" = true ]; then
            magick "$full_path" \
                \( +clone -alpha extract -draw 'fill black polygon 0,0 0,20 20,0 fill white circle 20,20 20,0' \
                   \( +clone -flip \) -compose Multiply -composite \
                   \( +clone -flop \) -compose Multiply -composite \
                \) -alpha off -compose CopyOpacity -composite "$temp_file" || mockup_success=false
        fi

        # Добавление тени
        if [ "$mockup_success" = true ]; then
            magick "$temp_file" \
                \( +clone -background black -shadow 60x20+0+10 -alpha set -channel A -evaluate multiply 1 +channel \) \
                +swap -background none -layers merge +repage "$mockup_file" || mockup_success=false
        fi

        if [ "$mockup_success" = true ] && [ -f "$mockup_file" ]; then
            rm "$temp_file"
            mv "$mockup_file" "$full_path"
            # Копируем обработанный файл в буфер
            if command -v wl-copy >/dev/null 2>&1; then
                wl-copy < "$full_path"
            elif command -v xclip >/dev/null 2>&1; then
                xclip -selection clipboard -t image/png < "$full_path"
            fi
        else
            echo "Warning: Mockup processing failed, keeping original." >&2
            rm -f "$temp_file" "$mockup_file"
            # Всё равно копируем оригинал (если mockup не удался)
            if [ "$mockup_mode" = "mockup" ]; then
                if command -v wl-copy >/dev/null 2>&1; then
                    wl-copy < "$full_path"
                elif command -v xclip >/dev/null 2>&1; then
                    xclip -selection clipboard -t image/png < "$full_path"
                fi
            fi
        fi
    fi

    # -------------------------------------------------
    # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: ждём 0.2 секунды, чтобы файл точно записался на диск
    # -------------------------------------------------
    sleep 0.2

    # Отправляем уведомление с действиями
    ACTION=$(notify-send -a "Ax-Shell" -i "$full_path" "Screenshot saved" "in $full_path" \
        -A "view=View" -A "edit=Edit" -A "open=Open Folder")

    # Обрабатываем нажатие на кнопки уведомления
    case "$ACTION" in
        view) xdg-open "$full_path" ;;
        edit) swappy -f "$full_path" ;;
        open) xdg-open "$save_dir" ;;
    esac
else
    # Если файл не создан (например, пользователь отменил выделение)
    notify-send -a "Ax-Shell" "Screenshot Aborted"
fi