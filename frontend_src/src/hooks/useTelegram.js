// Telegram WebApp
const tg = window.Telegram?.WebApp;

if (tg) {
  tg.expand();
  // tg.enableClosingConfirmation(); // Optional
  tg.disableVerticalSwipes();
}

export const useTelegram = () => {
  const user = tg?.initDataUnsafe?.user;

  // Fallback for development outside Telegram
  const userId = user?.id ? String(user.id) : "test_user";
  const username = user?.username || "Test User";

  return {
    tg,
    user,
    userId,
    username,
    close: () => tg?.close(),
  };
};
