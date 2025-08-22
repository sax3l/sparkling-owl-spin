// Backend connection status component
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useConnectionStatus } from "@/hooks/useApi";
import { Wifi, WifiOff, Server, ServerOff } from "lucide-react";

export function ConnectionStatus() {
  const { isOnline, backendConnected, status } = useConnectionStatus();
  
  const getStatusColor = () => {
    if (!isOnline) return "destructive";
    if (!backendConnected) return "destructive";
    return "success";
  };
  
  const getStatusText = () => {
    if (!isOnline) return "Offline";
    if (!backendConnected) return "Backend Disconnected";
    return "Connected";
  };
  
  const getIcon = () => {
    if (!isOnline) return <WifiOff className="h-3 w-3" />;
    if (!backendConnected) return <ServerOff className="h-3 w-3" />;
    return <Server className="h-3 w-3" />;
  };
  
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Badge 
          variant={getStatusColor() === "success" ? "default" : "destructive"}
          className="flex items-center gap-1 cursor-pointer"
        >
          {getIcon()}
          {getStatusText()}
        </Badge>
      </TooltipTrigger>
      <TooltipContent>
        <div className="text-sm">
          <div>Network: {isOnline ? "Online" : "Offline"}</div>
          <div>Backend: {backendConnected ? "Connected" : "Disconnected"}</div>
          {backendConnected && (
            <div className="text-xs text-muted-foreground mt-1">
              Backend API: http://localhost:8000
            </div>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
