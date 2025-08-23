import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  sv: {
    common: {
      "welcome": "Välkommen",
      "login": "Logga in",
      "logout": "Logga ut",
      "email": "E-post",
      "password": "Lösenord",
      "save": "Spara",
      "cancel": "Avbryt",
      "delete": "Ta bort",
      "edit": "Redigera",
      "create": "Skapa",
      "search": "Sök",
      "filter": "Filtrera",
      "loading": "Laddar...",
      "error": "Fel",
      "success": "Framgång",
      "settings": "Inställningar",
      "dashboard": "Instrumentpanel",
      "refresh": "Uppdatera"
    },
    dashboard: {
      "title": "ECaDP - Instrumentpanel",
      "overview": "Plattformsöversikt",
      "subtitle": "Övervaka dina etiska datainsamlingsoperationer",
      "activeJobs": "Aktiva jobb",
      "systemStatus": "Systemstatus",
      "quickActions": "Snabbåtgärder"
    },
    auth: {
      "loginTitle": "Logga in på ECaDP",
      "loginSubtitle": "Ange dina uppgifter för att komma åt plattformen",
      "signUp": "Registrera dig",
      "signIn": "Logga in"
    }
  },
  en: {
    common: {
      "welcome": "Welcome",
      "login": "Login",
      "logout": "Logout",
      "email": "Email",
      "password": "Password",
      "save": "Save",
      "cancel": "Cancel",
      "delete": "Delete",
      "edit": "Edit",
      "create": "Create",
      "search": "Search",
      "filter": "Filter",
      "loading": "Loading...",
      "error": "Error",
      "success": "Success",
      "settings": "Settings",
      "dashboard": "Dashboard",
      "refresh": "Refresh"
    },
    dashboard: {
      "title": "ECaDP - Dashboard",
      "overview": "Platform Overview",
      "subtitle": "Monitor your ethical data collection operations",
      "activeJobs": "Active Jobs",
      "systemStatus": "System Status",
      "quickActions": "Quick Actions"
    },
    auth: {
      "loginTitle": "Login to ECaDP",
      "loginSubtitle": "Enter your credentials to access the platform",
      "signUp": "Sign up",
      "signIn": "Sign in"
    }
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'sv', // default language
    fallbackLng: 'sv',
    
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
    
    react: {
      useSuspense: false,
    },

    detection: {
      // Options for language detection
      order: ['localStorage', 'navigator', 'htmlTag'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
  });

export default i18n;
