import pygame
import random
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Rock-Paper-Scissors - Fun 3D for Kids! 🎮")
CLOCK = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 60)
BUTTON_BG = (70, 130, 230)
BUTTON_HOVER = (100, 170, 255)
BUTTON_PRESSED = (50, 110, 210)
TEXT_COLOR = (255, 255, 255)
WIN_COLOR = (20, 220, 100)
LOSE_COLOR = (220, 50, 50)
TIE_COLOR = (240, 200, 60)
SCORE_BG = (50, 50, 90)
ANNOUNCEMENT_WIN = (0, 255, 120)
ANNOUNCEMENT_LOSE = (255, 100, 100)

# Fonts fixed sizes
pygame.font.init()
TITLE_FONT = pygame.font.SysFont("Comic Sans MS", 48, bold=True)
BUTTON_FONT = pygame.font.SysFont("Comic Sans MS", 28, bold=True)
RESULT_FONT = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
SCORE_FONT = pygame.font.SysFont("Comic Sans MS", 28, bold=True)
ANNOUNCEMENT_FONT = pygame.font.SysFont("Comic Sans MS", 32, bold=True)

# Attempt to load emoji font
try:
    EMOJI_FONT = pygame.font.SysFont("Segoe UI Emoji", 28)
    EMOJI_ANIM_FONT = pygame.font.SysFont("Segoe UI Emoji", 100)
except:
    EMOJI_FONT = BUTTON_FONT
    EMOJI_ANIM_FONT = pygame.font.SysFont(None, 100)

# Choices and their emojis
CHOICES = ["rock", "paper", "scissors"]
EMOJIS = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

# Helper function to draw text centered
def draw_text(surface, text, font, color, center):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=center)
    surface.blit(textobj, textrect)

# Button class with fixed size, no scaling animations
class Button:
    def __init__(self, x, y, width, height, text, emoji, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.emoji = emoji
        self.callback = callback
        self.hovered = False
        self.pressed = False

    def draw(self, surface):
        # Shadow for 3D effect
        shadow_rect = self.rect.copy()
        shadow_rect.move_ip(5, 5)
        pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=15)

        # Button color changes on hover and press
        if self.pressed:
            color = BUTTON_PRESSED
        elif self.hovered:
            color = BUTTON_HOVER
        else:
            color = BUTTON_BG

        # Draw main rect
        pygame.draw.rect(surface, color, self.rect, border_radius=15)

        # Highlight top third for 3D look
        highlight_rect = self.rect.copy()
        highlight_rect.height = self.rect.height // 3
        pygame.draw.rect(surface, (100, 170, 255), highlight_rect, border_radius=15)

        # Draw emoji using EMOJI_FONT for better emoji support
        emoji_surface = EMOJI_FONT.render(self.emoji, True, TEXT_COLOR)
        emoji_rect = emoji_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
        surface.blit(emoji_surface, emoji_rect)

        draw_text(surface, self.text, BUTTON_FONT, TEXT_COLOR, (self.rect.centerx, self.rect.centery + 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.callback()
            self.pressed = False

# Choice Animation with fixed emoji size, no scaling animation
class ChoiceAnimation:
    def __init__(self, x, y, emoji):
        self.x = x
        self.y = y
        self.emoji = emoji
        self.start_time = pygame.time.get_ticks()
        self.duration = 700  # ms
        self.finished = False

    def draw(self, surface):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            self.finished = True
        # Draw emoji at fixed size 100 px font
        emoji_surf = EMOJI_ANIM_FONT.render(self.emoji, True, WHITE)
        rect = emoji_surf.get_rect(center=(self.x, self.y))
        surface.blit(emoji_surf, rect)

# Main game class
class RockPaperScissorsGame:
    def __init__(self):
        self.score = {"You": 0, "Computer": 0}
        self.user_choice = None
        self.comp_choice = None
        self.result = ""
        self.result_color = WHITE
        self.animations = []
        self.announcement = ""
        self.announcement_color = WHITE

        btn_width, btn_height = 160, 120
        spacing = 40
        start_x = (WIDTH - (btn_width * 3 + spacing * 2)) // 2
        y_pos = HEIGHT - btn_height - 120  # moved up 60px to avoid cutoff

        self.buttons = []
        # Fix late binding in lambda by default arg
        for i, choice in enumerate(CHOICES):
            btn = Button(
                start_x + i * (btn_width + spacing),
                y_pos,
                btn_width,
                btn_height,
                choice.capitalize(),
                EMOJIS[choice],
                callback = self.make_callback(choice)
            )
            self.buttons.append(btn)

        # Score box fixed below buttons with margin so no cutoff
        self.score_box_rect = pygame.Rect(start_x, y_pos + btn_height + 10, btn_width * 3 + spacing * 2, 80)

    def make_callback(self, choice):
        return lambda: self.play_round(choice)

    def play_round(self, user_choice):
        if any(anim.finished == False for anim in self.animations):
            return

        comp_choice = random.choice(CHOICES)
        self.user_choice = user_choice
        self.comp_choice = comp_choice

        if user_choice == comp_choice:
            self.result = "It's a Tie! 🤝"
            self.result_color = TIE_COLOR
            self.announcement = ""
        elif (user_choice == "rock" and comp_choice == "scissors") or \
             (user_choice == "paper" and comp_choice == "rock") or \
             (user_choice == "scissors" and comp_choice == "paper"):
            self.result = "You Win! 🎉"
            self.result_color = WIN_COLOR
            self.score["You"] += 1
            self.announcement = "🎉 Congratulations! You Won! 🎉"
            self.announcement_color = ANNOUNCEMENT_WIN
        else:
            self.result = "You Lose! 😞"
            self.result_color = LOSE_COLOR
            self.score["Computer"] += 1
            self.announcement = "😢 Oh no! You Lost! 😢"
            self.announcement_color = ANNOUNCEMENT_LOSE

        self.animations = [
            ChoiceAnimation(WIDTH // 3, HEIGHT // 3, EMOJIS[user_choice]),
            ChoiceAnimation(2 * WIDTH // 3, HEIGHT // 3, EMOJIS[comp_choice])
        ]

    def update(self):
        self.animations = [anim for anim in self.animations if not anim.finished]

    def draw(self, surface):
        surface.fill(BG_COLOR)

        draw_text(surface, "Rock-Paper-Scissors!", TITLE_FONT, WHITE, (WIDTH // 2, 70))

        draw_text(surface, "Choose your move below:", BUTTON_FONT, WHITE, (WIDTH // 2, 120))

        for btn in self.buttons:
            btn.draw(surface)

        for anim in self.animations:
            anim.draw(surface)

        if not self.animations and self.result != "":
            draw_text(surface, self.result, RESULT_FONT, self.result_color, (WIDTH // 2, HEIGHT // 2))

        pygame.draw.rect(surface, SCORE_BG, self.score_box_rect, border_radius=20)
        draw_text(surface, f"Score  |  You: {self.score['You']}  -  Computer: {self.score['Computer']}",
                  SCORE_FONT, WHITE, self.score_box_rect.center)

        if self.announcement:
            announcement_center = (WIDTH // 2, self.score_box_rect.bottom + 40)
            draw_text(surface, self.announcement, ANNOUNCEMENT_FONT, self.announcement_color, announcement_center)

def main():
    game = RockPaperScissorsGame()

    running = True
    while running:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            for btn in game.buttons:
                btn.handle_event(event)

        game.update()
        game.draw(SCREEN)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

