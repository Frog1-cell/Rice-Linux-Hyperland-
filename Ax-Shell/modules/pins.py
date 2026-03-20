import gi
import math

import config.data as data

gi.require_version('Gtk', '3.0')
import json
import os
import subprocess
import time
import glob
from pathlib import Path

import cairo
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, GObject
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.scrolledwindow import ScrolledWindow
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk
from gi.repository import Pango

import modules.icons as icons

SAVE_FILE = os.path.expanduser("~/.theme_state.json")

# Размер иконок в зависимости от положения панели
icon_size = 80
if data.PANEL_THEME == "Panel" and data.BAR_POSITION in ["Left", "Right"] or data.PANEL_POSITION in ["Start", "End"]:
    icon_size = 48

class ThemeManager:
    """Встроенный менеджер тем с функциями переключения"""
    
    def __init__(self):
        self.state_file = os.path.expanduser("~/.wallpaper_state")
        self.config_dirs = {
            'rofi': os.path.expanduser("~/.config/rofi/themes"),
            'alacritty': os.path.expanduser("~/.config/alacritty"),
            'hypr': os.path.expanduser("~/.config/hypr"),
            'ax': os.path.expanduser("~/.config/Ax-Shell"),
            'zsh': os.path.expanduser("~/.config/zsh"),
        }
        
        # Создаем необходимые директории если их нет
        for dir_path in self.config_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Определение тем (добавьте поле 'type' для работы с neovim)
        self.themes = [
            {
                'id': 0,
                'name': 'Ми Фу',
                'type': 'dark',
                'wallpaper': '~/.config/Ax-Shell/wallpaper/Arknights: Enfield/Ми Фу',
                'icon': 'weather-clear-night',
                'transition': 'wipe',
                'transition_pos': 'top-right',
                'duration': 3,
                'configs': {
                    'rofi': 'hyperland_custom.rasi',
                    'alacritty': 'theme_dark.toml',
                    'hypr': 'border_dark.conf',
                    'ax': 'styles_1',
                    'zsh': 'theme_mifu.zsh'
                }
            },
            {
                'id': 1,
                'name': 'Джуань',
                'type': 'light',
                'wallpaper': '~/.config/Ax-Shell/wallpaper/Arknights: Enfield/Чжуань Фаньи',
                'icon': 'weather-clear',
                'transition': 'wipe',
                'transition_pos': 'top-right',
                'duration': 3,
                'configs': {
                    'rofi': 'hyperland_custom_2.rasi',
                    'alacritty': 'theme_light.toml',
                    'hypr': 'border_light.conf',
                    'ax': 'styles_2',
                    'zsh': 'theme_zhuan.zsh'
                }
            },
            {
                'id': 2,
                'name': 'Лэватайн',
                'type': 'dark',
                'wallpaper': '~/.config/Ax-Shell/wallpaper/Arknights: Enfield/Лэватайн',
                'icon': 'weather-storm',
                'transition': 'wipe',
                'transition_pos': 'center',
                'duration': 3,
                'configs': {
                    'rofi': 'hyperland_custom_leva.rasi',
                    'alacritty': 'theme_leva.toml',
                    'hypr': 'border_leva.conf',
                    'ax': 'Ми Фу',
                    'zsh': 'theme_leva.zsh'
                }
            },
            {
                'id': 3,
                'name': 'Ивонна',
                'type': 'light',
                'wallpaper': '~/.config/Ax-Shell/wallpaper/Arknights: Enfield/Ивонна',
                'icon': 'weather-few-clouds',
                'transition': 'wipe',
                'transition_pos': 'top',
                'duration': 3,
                'configs': {
                    'rofi': 'hyperland_custom_yvonne.rasi',
                    'alacritty': 'theme_yvonne.toml',
                    'hypr': 'border_yvonne.conf',
                    'ax': 'Ми Фу',
                    'zsh': 'theme_yvonne.zsh'
                }
            },
            {
                'id': 4,
                'name': 'Гилберта',
                'type': 'dark',
                'wallpaper': '~/.config/Ax-Shell/wallpaper/Arknights: Enfield/Гилберта',
                'icon': 'weather-showers-scattered',
                'transition': 'wipe',
                'transition_pos': 'bottom-right',
                'duration': 3,
                'configs': {
                    'rofi': 'hyperland_custom_gil.rasi',
                    'alacritty': 'theme_gil.toml',
                    'hypr': 'border_gil.conf',
                    'ax': 'Ми Фу',
                    'zsh': 'theme_gil.zsh'
                }
            },
            {
                'id': 5,
                'name': 'Е Шуньгуан',
                'type': 'dark',
                'wallpaper': '~/.config/Ax-Shell/wallpaper/ZZZ/Е Шуньгуан',
                'icon': 'weather-showers-scattered',
                'transition': 'wipe',
                'transition_pos': 'bottom-right',
                'duration': 3,
                'configs': {
                    'rofi': 'hyperland_custom_gil.rasi',
                    'alacritty': 'theme_gil.toml',
                    'hypr': 'border_gil.conf',
                    'ax': 'Ми Фу',
                    'zsh': 'theme_gil.zsh'
                }
            }
        ]
        
    def get_current_theme(self):
        """Получить текущую тему (индекс)"""
        try:
            with open(self.state_file, 'r') as f:
                return int(f.read().strip())
        except:
            return 0
            
    def get_theme_by_id(self, theme_id):
        """Получить тему по ID"""
        for theme in self.themes:
            if theme['id'] == theme_id:
                return theme
        return self.themes[0]
    
    def reload_nvim_theme(self, theme_type):
        """Переключить тему во всех запущенных Neovim"""
        try:
            # Ищем все запущенные серверы Neovim
            socket_patterns = [
                '/tmp/nvim.*',
                f"/run/user/{os.getuid()}/nvim.*"
            ]
            
            for pattern in socket_patterns:
                for sock in glob.glob(pattern):
                    if os.path.exists(sock) and not os.path.isdir(sock):
                        try:
                            subprocess.run(
                                ['nvim', '--server', sock, '--remote-send', 
                                 f'<C-\\><C-n>:lua vim.o.background="{theme_type}"<CR>:lua require("theme").setup()<CR>'],
                                timeout=1,
                                capture_output=True
                            )
                        except:
                            pass
        except Exception as e:
            print(f"Error reloading nvim theme: {e}")
    
    def apply_theme(self, theme_id):
        """Применить тему по ID"""
        theme = self.get_theme_by_id(theme_id)
        if not theme:
            return False
            
        try:
            wallpaper = os.path.expanduser(theme['wallpaper'])
            
            # Проверяем существует ли файл обоев
            if not os.path.exists(wallpaper):
                print(f"Wallpaper not found: {wallpaper}")
                # Пробуем найти файл без учета регистра
                wallpaper_dir = os.path.dirname(wallpaper)
                wallpaper_name = os.path.basename(wallpaper)
                if os.path.exists(wallpaper_dir):
                    for f in os.listdir(wallpaper_dir):
                        if f.lower() == wallpaper_name.lower():
                            wallpaper = os.path.join(wallpaper_dir, f)
                            break
            
            # Смена обоев через swww
            swww_cmd = [
                'swww', 'img', wallpaper,
                '--transition-type', theme['transition'],
                '--transition-pos', theme['transition_pos'],
                '--transition-step', '75',
                '--transition-duration', str(theme['duration']),
                '--transition-fps', '50'
            ]
            
            # Запускаем смену обоев
            subprocess.run(swww_cmd, capture_output=True)
            
            # Небольшая задержка для применения обоев
            time.sleep(1)
            
            # Применяем конфигурации для каждого компонента
            configs = theme['configs']
            
            # Rofi
            rofi_source = os.path.join(self.config_dirs['rofi'], configs['rofi'])
            rofi_target = os.path.join(self.config_dirs['rofi'], 'current.rasi')
            if os.path.exists(rofi_source):
                try:
                    if os.path.exists(rofi_target) or os.path.islink(rofi_target):
                        os.remove(rofi_target)
                    os.symlink(rofi_source, rofi_target)
                    subprocess.run(['pkill', '-x', 'rofi'], capture_output=True)
                except Exception as e:
                    print(f"Error setting rofi theme: {e}")
            
            # Alacritty
            alacritty_source = os.path.join(self.config_dirs['alacritty'], configs['alacritty'])
            alacritty_target = os.path.join(self.config_dirs['alacritty'], 'theme.toml')
            if os.path.exists(alacritty_source):
                try:
                    if os.path.exists(alacritty_target) or os.path.islink(alacritty_target):
                        os.remove(alacritty_target)
                    os.symlink(alacritty_source, alacritty_target)
                    subprocess.run(['alacritty', 'msg', 'config-reload'], capture_output=True)
                except Exception as e:
                    print(f"Error setting alacritty theme: {e}")
            
            # Hyprland
            hypr_source = os.path.join(self.config_dirs['hypr'], configs['hypr'])
            hypr_target = os.path.join(self.config_dirs['hypr'], 'border.conf')
            if os.path.exists(hypr_source):
                try:
                    if os.path.exists(hypr_target) or os.path.islink(hypr_target):
                        os.remove(hypr_target)
                    os.symlink(hypr_source, hypr_target)
                    subprocess.run(['hyprctl', 'reload'], capture_output=True)
                except Exception as e:
                    print(f"Error setting hypr theme: {e}")
            
            # Ax-Shell
            ax_source = os.path.join(self.config_dirs['ax'], configs['ax'])
            ax_target = os.path.join(self.config_dirs['ax'], 'styles')
            if os.path.exists(ax_source):
                try:
                    if os.path.exists(ax_target) or os.path.islink(ax_target):
                        os.remove(ax_target)
                    os.symlink(ax_source, ax_target, target_is_directory=True)
                    subprocess.run(['fabric-cli', 'exec', 'ax-shell', 'app.set_css()'], 
                                 capture_output=True)
                except Exception as e:
                    print(f"Error setting ax-shell theme: {e}")
            
            # Zsh
            zsh_theme_dir = os.path.join(self.config_dirs['zsh'], 'themes')
            os.makedirs(zsh_theme_dir, exist_ok=True)
            zsh_source = os.path.join(zsh_theme_dir, configs['zsh'])
            zsh_target = os.path.join(self.config_dirs['zsh'], 'current_theme.zsh')
            if os.path.exists(zsh_source):
                try:
                    if os.path.exists(zsh_target) or os.path.islink(zsh_target):
                        os.remove(zsh_target)
                    os.symlink(zsh_source, zsh_target)
                except Exception as e:
                    print(f"Error setting zsh theme: {e}")
            
            # Neovim
            self.reload_nvim_theme(theme['type'])
            
            # Сохраняем состояние
            with open(self.state_file, 'w') as f:
                f.write(str(theme_id))
            
            return True
            
        except Exception as e:
            print(f"Error applying theme: {e}")
            return False
    
    def toggle_theme(self):
        """Переключить на следующую тему по кругу"""
        current = self.get_current_theme()
        next_id = (current + 1) % len(self.themes)
        return self.apply_theme(next_id)

class ThemeCell(Gtk.EventBox):
    """Ячейка темы в списке (без иконки, только название)"""
    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }
    
    def __init__(self, app, theme_data):
        super().__init__(name="theme-cell")
        self.app = app
        self.theme_data = theme_data
        self.is_active_state = False
        self.is_selected_state = False
        
        # Основной контейнер
        self.box = Box(name="theme-cell-box", orientation="h", spacing=12)
        self.add(self.box)
        
        # Название темы
        self.name_label = Label(
            name="theme-name",
            label=theme_data['name'],
            justification="left",
            ellipsization="end",
            style="font-weight: bold; font-size: 16px;"
        )
        self.box.pack_start(self.name_label, True, True, 0)
        
        # Обработчики событий
        self.connect("button-press-event", self.on_click)
        self.update_style()
    
    def update_style(self):
        """Обновить стиль на основе состояний"""
        if self.is_selected_state:
            self.set_name("theme-cell-selected")
        elif self.is_active_state:
            self.set_name("theme-cell-active")
        else:
            self.set_name("theme-cell")
    
    def set_active(self, is_active):
        """Установить активное состояние темы (применена в системе)"""
        if self.is_active_state != is_active:
            self.is_active_state = is_active
            self.update_style()
    
    def set_selected(self, is_selected):
        """Установить выделение для предпросмотра"""
        if self.is_selected_state != is_selected:
            self.is_selected_state = is_selected
            self.update_style()
    
    def on_click(self, widget, event):
        if event.button == 1:  # Левый клик
            self.app.select_theme(self.theme_data['id'])
        return True

class ImageCover(Gtk.DrawingArea):
    """Виджет для отображения изображения с масштабированием cover и скруглёнными углами"""
    def __init__(self, radius=16):
        super().__init__()
        self.pixbuf = None
        self.radius = radius
        self.connect("draw", self.on_draw)
    
    def set_pixbuf(self, pixbuf):
        self.pixbuf = pixbuf
        self.queue_draw()
    
    def _rounded_rectangle(self, cr, x, y, width, height, radius):
        """Добавляет прямоугольник со скруглёнными углами к текущему пути"""
        cr.move_to(x + radius, y)
        cr.line_to(x + width - radius, y)
        cr.arc(x + width - radius, y + radius, radius, -math.pi / 2, 0)
        cr.line_to(x + width, y + height - radius)
        cr.arc(x + width - radius, y + height - radius, radius, 0, math.pi / 2)
        cr.line_to(x + radius, y + height)
        cr.arc(x + radius, y + height - radius, radius, math.pi / 2, math.pi)
        cr.line_to(x, y + radius)
        cr.arc(x + radius, y + radius, radius, math.pi, 3 * math.pi / 2)
        cr.close_path()
    
    def on_draw(self, widget, cr):
        if not self.pixbuf:
            return False
        allocation = self.get_allocation()
        width = allocation.width
        height = allocation.height
        img_w = self.pixbuf.get_width()
        img_h = self.pixbuf.get_height()
        if width <= 0 or height <= 0 or img_w <= 0 or img_h <= 0:
            return False
        
        # Масштабируем для покрытия всей области (cover)
        scale = max(width / img_w, height / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        x = (width - draw_w) / 2
        y = (height - draw_h) / 2
        
        # Масштабируем pixbuf до нужного размера
        scaled_pixbuf = self.pixbuf.scale_simple(int(draw_w), int(draw_h), GdkPixbuf.InterpType.BILINEAR)
        
        # Обрезаем скруглёнными углами
        self._rounded_rectangle(cr, 0, 0, width, height, self.radius)
        cr.clip()
        
        # Рисуем изображение
        Gdk.cairo_set_source_pixbuf(cr, scaled_pixbuf, x, y)
        cr.paint()
        
        # Сбрасываем clip для следующих отрисовок
        cr.reset_clip()
        return True

class ThemePreview(Gtk.Box):
    """Виджет предпросмотра обоев"""
    def __init__(self, theme_manager):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.theme_manager = theme_manager
        self.current_theme_id = None
        self.preview_cache = {}  # Кэш для загруженных изображений
        
        # Заголовок
        self.preview_label = Label(
            name="preview-label",
            label="Предпросмотр",
            justification="center",
            style="font-size: 18px; font-weight: bold;"
        )
        self.pack_start(self.preview_label, False, False, 0)
        
        # Контейнер для изображения (уменьшенный размер)
        self.image_container = Box(name="preview-image-container", orientation="v")
        self.image_container.set_size_request(600, 400)  # Уменьшили размеры
        self.pack_start(self.image_container, True, True, 0)
        
        # Изначально пустое изображение
        self.image_cover = None
        self.show_placeholder()
        
        # Таймер для debounce обновлений
        self.update_timeout_id = None
        
    def show_placeholder(self):
        """Показать заглушку, если нет изображения"""
        if self.image_cover:
            self.image_container.remove(self.image_cover)
            self.image_cover = None
        
        label = Label(
            name="preview-placeholder",
            label="Выберите тему для предпросмотра",
            justification="center",
            style="font-size: 16px; opacity: 0.6; padding: 30px;"
        )
        self.image_container.pack_start(label, True, True, 0)
        self.image_container.show_all()
    
    def load_preview_async(self, theme_id):
        """Асинхронная загрузка предпросмотра"""
        if theme_id == self.current_theme_id:
            return  # Уже загружаем эту тему
        
        self.current_theme_id = theme_id
        theme = self.theme_manager.get_theme_by_id(theme_id)
        wallpaper_path = os.path.expanduser(theme['wallpaper'])
        
        # Проверяем кэш
        if wallpaper_path in self.preview_cache:
            self.display_pixbuf(self.preview_cache[wallpaper_path])
            return
        
        # Загружаем в отдельном потоке
        def load_thread(_):
            try:
                if os.path.exists(wallpaper_path):
                    # Загружаем с размерами контейнера для экономии ресурсов
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        wallpaper_path,
                        width=600, height=400,
                        preserve_aspect_ratio=True
                    )
                    # Сохраняем в кэш
                    self.preview_cache[wallpaper_path] = pixbuf
                    # Ограничиваем размер кэша (оставляем последние 3)
                    if len(self.preview_cache) > 3:
                        # Удаляем самый старый
                        oldest = next(iter(self.preview_cache))
                        del self.preview_cache[oldest]
                    
                    GLib.idle_add(self.display_pixbuf, pixbuf)
                else:
                    GLib.idle_add(self.show_error, f"Файл не найден:\n{os.path.basename(wallpaper_path)}")
            except Exception as e:
                print(f"Error loading preview: {e}")
                GLib.idle_add(self.show_error, "Ошибка загрузки\nизображения")
        
        GLib.Thread.new("preview-load", load_thread, None)
    
    def display_pixbuf(self, pixbuf):
        """Отобразить загруженное изображение (вызывается в основном потоке)"""
        if not pixbuf:
            return
            
        # Убираем предыдущее содержимое
        for child in self.image_container.get_children():
            self.image_container.remove(child)
        
        # Создаём и добавляем виджет с обложкой
        self.image_cover = ImageCover(radius=16)  # скругление 16px
        self.image_cover.set_pixbuf(pixbuf)
        self.image_cover.set_vexpand(True)
        self.image_cover.set_hexpand(True)
        self.image_container.pack_start(self.image_cover, True, True, 0)
        self.image_container.show_all()
    
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        for child in self.image_container.get_children():
            self.image_container.remove(child)
        
        label = Label(
            name="preview-error",
            label=message,
            justification="center",
            style="font-size: 14px; opacity: 0.6; padding: 30px;"
        )
        self.image_container.pack_start(label, True, True, 0)
        self.image_container.show_all()
    
    def update_preview(self, theme_id):
        """Обновить предпросмотр для темы (с debounce)"""
        # Отменяем предыдущий запрос на обновление
        if self.update_timeout_id:
            GLib.source_remove(self.update_timeout_id)
            self.update_timeout_id = None
        
        # Запускаем с небольшой задержкой (для избежания множественных обновлений при скролле)
        self.update_timeout_id = GLib.timeout_add(50, self.do_update_preview, theme_id)
    
    def do_update_preview(self, theme_id):
        """Фактическое обновление предпросмотра"""
        self.update_timeout_id = None
        self.load_preview_async(theme_id)
        return False
    
    def on_apply_clicked(self):
        """Применить выбранную тему (вызывается из обработчика клавиш)"""
        if self.current_theme_id is not None:
            # Функция для потока
            def apply_thread(_):
                if self.theme_manager.apply_theme(self.current_theme_id):
                    GLib.idle_add(self.on_theme_applied)
            
            GLib.Thread.new("theme-apply", apply_thread, None)
    
    def on_theme_applied(self):
        """Обновить состояние после применения (можно добавить уведомление)"""
        pass

class Themes(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        
        self.theme_manager = ThemeManager()
        self.cells = []
        self.current_theme_id = self.theme_manager.get_current_theme()
        self.selected_index = self.current_theme_id
        self.filter_text = ""
        
        # Левая панель - список тем
        left_panel = Box(name="themes-left-panel", orientation="v", spacing=10)
        left_panel.set_size_request(400, -1)
        
        # Заголовок списка
        left_panel.pack_start(
            Label(name="themes-list-title", label="Список тем", 
                 justification="center", style="font-size: 18px; font-weight: bold;"),
            False, False, 10
        )
        
        # Поисковая строка (всегда видна, но активируется по нажатию 'l')
        search_box = Box(name="search-box", orientation="h", spacing=5)
        search_icon = Label(name="search-icon", label="🔍", style="font-size: 16px;")
        search_box.pack_start(search_icon, False, False, 5)
        
        self.search_entry = Gtk.Entry(name="search-entry")
        self.search_entry.set_placeholder_text("Поиск тем...")
        self.search_entry.connect("changed", self.on_search_changed)
        # Обработка клавиш в поле поиска
        self.search_entry.connect("key-press-event", self.on_search_key_press)
        search_box.pack_start(self.search_entry, True, True, 0)
        
        left_panel.pack_start(search_box, False, False, 5)
        
        # Контейнер с прокруткой для списка тем
        self.themes_scroll = Gtk.ScrolledWindow()
        self.themes_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.themes_scroll.set_vexpand(True)
        
        self.themes_list = Box(name="themes-list", orientation="v", spacing=8)
        self.themes_scroll.add(self.themes_list)
        left_panel.pack_start(self.themes_scroll, True, True, 0)
        
        # Подсказка по управлению
        hint_label = Label(
            name="navigation-hint",
            label="↑/↓ - навигация, Enter/→ - применить, L - поиск",
            justification="center",
            style="font-size: 14px; opacity: 0.7; padding: 10px;"
        )
        left_panel.pack_start(hint_label, False, False, 0)
        
        # Правая панель - предпросмотр
        right_panel = ThemePreview(self.theme_manager)
        right_panel.set_size_request(650, -1)  # Ширина под новый размер превью
        
        # Собираем всё вместе
        self.pack_start(left_panel, False, False, 0)
        self.pack_start(right_panel, True, True, 0)
        
        # Создаём ячейки для всех тем
        self.all_cells = []
        for i, theme_data in enumerate(self.theme_manager.themes):
            theme_data['is_active'] = (theme_data['id'] == self.current_theme_id)
            cell = ThemeCell(self, theme_data)
            self.all_cells.append(cell)
        
        # Изначально показываем все
        self.filter_themes()
        
        # Устанавливаем начальное выделение
        self.update_selection(self.selected_index)
        
        # Настройка фокуса для клавиатурной навигации
        self.set_can_focus(True)
        self.connect("key-press-event", self.on_key_press)
        GLib.idle_add(self.grab_focus)
        
        # Мониторинг изменений состояния темы (реже, чтобы не нагружать)
        GLib.timeout_add_seconds(5, self.check_theme_state)
    
    def on_search_changed(self, entry):
        """Обработка изменения текста поиска"""
        self.filter_text = entry.get_text().lower()
        # Используем idle_add для отложенного выполнения фильтрации
        if hasattr(self, '_filter_timeout') and self._filter_timeout is not None:
            GLib.source_remove(self._filter_timeout)
        self._filter_timeout = GLib.timeout_add(150, self.filter_themes)
    
    def filter_themes(self):
        """Фильтровать список тем по тексту поиска"""
        self._filter_timeout = None
        
        # Очищаем список
        for child in self.themes_list.get_children():
            self.themes_list.remove(child)
        
        self.cells = []
        
        # Добавляем только те, что проходят фильтр
        for cell in self.all_cells:
            theme_name = cell.theme_data['name'].lower()
            if self.filter_text in theme_name:
                self.cells.append(cell)
                self.themes_list.pack_start(cell, False, False, 0)
        
        self.themes_list.show_all()
        
        # Если после фильтрации выделенный индекс вне диапазона, сбрасываем на первый
        if self.cells:
            if self.selected_index >= len(self.cells):
                self.selected_index = 0
            self.update_selection(self.selected_index)
            if self.cells:
                first_id = self.cells[0].theme_data['id']
                right_panel = self.get_children()[1]
                right_panel.update_preview(first_id)
            self.scroll_to_selected()
        else:
            self.selected_index = -1
            right_panel = self.get_children()[1]
            right_panel.show_placeholder()
        
        return False
    
    def select_theme(self, theme_id):
        """Выбрать тему для предпросмотра (без применения)"""
        for i, cell in enumerate(self.cells):
            if cell.theme_data['id'] == theme_id:
                self.selected_index = i
                self.update_selection(i)
                right_panel = self.get_children()[1]
                right_panel.update_preview(theme_id)
                self.scroll_to_selected()
                break
    
    def update_selection(self, index):
        """Обновить визуальное выделение ячеек"""
        for i, cell in enumerate(self.cells):
            cell.set_selected(i == index)
    
    def scroll_to_selected(self):
        """Прокрутить список так, чтобы выбранная ячейка была видима"""
        if not self.cells or self.selected_index < 0 or self.selected_index >= len(self.cells):
            return
        cell = self.cells[self.selected_index]
        # Проверяем, что ячейка уже отрисована
        if not cell.get_realized():
            GLib.idle_add(self.scroll_to_selected)
            return
        cell_allocation = cell.get_allocation()
        cell_height = cell_allocation.height
        if cell_height <= 0:
            GLib.idle_add(self.scroll_to_selected)
            return
        
        vadj = self.themes_scroll.get_vadjustment()
        page_size = vadj.get_page_size()
        # Расстояние между ячейками (spacing=8)
        spacing = 8
        # Позиция верхнего края ячейки относительно начала списка
        y_pos = self.selected_index * (cell_height + spacing)
        # Если ячейка выше видимой области
        if y_pos < vadj.get_value():
            vadj.set_value(y_pos)
        # Если ячейка ниже видимой области
        elif y_pos + cell_height > vadj.get_value() + page_size:
            vadj.set_value(y_pos + cell_height - page_size)
    
    def on_key_press(self, widget, event):
        """Обработка нажатий клавиш"""
        keyval = event.keyval
        
        # Активация поиска по 'l'
        if keyval == Gdk.KEY_l or keyval == Gdk.KEY_L:
            # Если фокус не в поле поиска, то перевести фокус
            if not self.search_entry.has_focus():
                self.search_entry.grab_focus()
                self.search_entry.set_text("")
                self.search_entry.select_region(0, -1)  # выделить весь текст
            return True
        
        # Если фокус в поле поиска, не обрабатываем навигацию по списку
        if self.search_entry.has_focus():
            return False
        
        if not self.cells:
            return False
            
        if keyval == Gdk.KEY_Up:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_selection(self.selected_index)
                theme_id = self.cells[self.selected_index].theme_data['id']
                right_panel = self.get_children()[1]
                right_panel.update_preview(theme_id)
                self.scroll_to_selected()
            return True
        elif keyval == Gdk.KEY_Down:
            if self.selected_index < len(self.cells) - 1:
                self.selected_index += 1
                self.update_selection(self.selected_index)
                theme_id = self.cells[self.selected_index].theme_data['id']
                right_panel = self.get_children()[1]
                right_panel.update_preview(theme_id)
                self.scroll_to_selected()
            return True
        elif keyval in (Gdk.KEY_Right, Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self.selected_index >= 0:
                right_panel = self.get_children()[1]
                right_panel.on_apply_clicked()
            return True
        return False
    
    def on_search_key_press(self, widget, event):
        """Обработка клавиш в поле поиска"""
        if event.keyval == Gdk.KEY_Escape:
            # Очищаем поиск и возвращаем фокус на список
            widget.set_text("")
            self.grab_focus()
            return True
        return False
    
    def check_theme_state(self):
        """Проверить изменилось ли состояние темы извне"""
        new_state = self.theme_manager.get_current_theme()
        if new_state != self.current_theme_id:
            self.current_theme_id = new_state
            self.update_active_state()
        return True
    
    def update_active_state(self):
        """Обновить активное состояние всех ячеек"""
        for cell in self.all_cells:
            is_active = (cell.theme_data['id'] == self.current_theme_id)
            cell.set_active(is_active)
    
    def stop_monitoring(self):
        """Остановка мониторинга (вызывается при закрытии)"""
        pass

# Для обратной совместимости
Pins = Themes
