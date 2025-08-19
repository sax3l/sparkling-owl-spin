import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlayCircle,
  FileText,
  DatabaseZap,
  Download,
  Trash2,
  ShieldCheck,
  Code,
  Settings,
} from 'lucide-react';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/launch', label: 'Job Launcher', icon: PlayCircle },
  { href: '/templates', label: 'Template Builder', icon: FileText },
  { href: '/dq', label: 'DQ Panel', icon: DatabaseZap },
  { href: '/exports', label: 'Exports', icon: Download },
  { href: '/erasure', label: 'Erasure Admin', icon: Trash2 },
  { href: '/proxies', label: 'Proxy Monitor', icon: ShieldCheck },
  { href: '/api', label: 'API Explorer', icon: Code },
  { href: '/settings', label: 'Settings', icon: Settings },
];

interface SidebarProps {
  isOpen: boolean;
}

const Sidebar = ({ isOpen }: SidebarProps) => {
  return (
    <aside
      className={`bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white w-64 min-h-screen p-4 transform ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 transition-transform duration-300 ease-in-out fixed md:relative z-20`}
    >
      <nav>
        <ul>
          {navItems.map((item) => (
            <li key={item.href} className="mb-2">
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 ${
                    isActive ? 'bg-gray-300 dark:bg-gray-900 font-bold' : ''
                  }`
                }
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;