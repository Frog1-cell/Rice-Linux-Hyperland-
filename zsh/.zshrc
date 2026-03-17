export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME=""

plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

function get_current_path() {
    echo -n "%~"
}

PROMPT='$(get_current_path) ❯ '
DISABLE_AUTO_TITLE="true"


export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

load_theme() {
    if [[ -f "$HOME/.config/zsh/current_theme.zsh" ]]; then
        source "$HOME/.config/zsh/current_theme.zsh"
    fi
    command -v zle >/dev/null 2>&1 && zle reset-prompt 2>/dev/null
}

load_theme

if command -v inotifywait >/dev/null 2>&1; then
    zsh_theme_watcher() {
        while inotifywait -e CLOSE_WRITE "$HOME/.config/zsh/current_theme.zsh" >/dev/null 2>&1; do
            load_theme
        done
    }
    pkill -f "inotifywait.*current_theme.zsh" 2>/dev/null
    zsh_theme_watcher & 
fi

HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY

alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -A'

autoload -U add-zsh-hook
function chpwd_update_prompt() {
    zle reset-prompt 2>/dev/null
}
add-zsh-hook chpwd chpwd_update_prompt
