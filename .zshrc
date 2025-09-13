autoload -Uz vcs_info
precmd() { vcs_info }

zstyle ':vcs_info:git:*' formats '⟮%b⟯'

setopt PROMPT_SUBST
PROMPT='%(?,,%F{red}%?%f )[${AWS_PROFILE}]%F{010}%*%f %F{003}%~%f%F{006}${vcs_info_msg_0_}%f:'
# PROMPT='%(?,,%F{red}%?%f )%K{blue}%F{white}%*%f%k %F{003}%~%f%F{006}${vcs_info_msg_0_}%f:'


# Startup commands



#ALIAS
alias ls='ls --color=auto'

export PATH="$HOME/.local/bin:$HOME/bin::$PATH"
