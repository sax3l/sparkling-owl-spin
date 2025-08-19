import { Menu } from 'lucide-react';

interface HeaderProps {
  toggleSidebar: () => void;
}

const Header = ({ toggleSidebar }: HeaderProps) => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-md p-4 flex items-center">
      <button onClick={toggleSidebar} className="md:hidden mr-4">
        <Menu />
      </button>
      <h1 className="text-xl font-semibold">Ethical Crawler & Data Platform</h1>
    </header>
  );
};

export default Header;