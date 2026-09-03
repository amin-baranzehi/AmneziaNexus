from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from .models import AmneziaConfig
from .forms import AmneziaConfigForm
from .services import VPNManager, PingService, LogService

class DashboardView(LoginRequiredMixin, ListView):
    """Main dashboard view displaying all configurations."""
    model = AmneziaConfig
    template_name = 'vpn_panel/dashboard.html'
    context_object_name = 'configs'

    def get_context_data(self, **kwargs):
        """Inject system connection status into context."""
        context = super().get_context_data(**kwargs)
        
        # Verify the actual system status
        is_system_connected = VPNManager.is_connected()
        context['is_system_connected'] = is_system_connected
        
        # Sync DB state with reality if needed
        active_config = AmneziaConfig.objects.filter(is_active=True).first()
        if active_config and not is_system_connected:
            active_config.is_active = False
            active_config.save()
        elif not active_config and is_system_connected:
            # The interface is up but no DB record claims to be active.
            context['system_warning'] = "VPN is active on the OS, but no profile is marked active in the panel."
            
        context['form'] = AmneziaConfigForm()
        return context

class ConfigCreateView(LoginRequiredMixin, CreateView):
    """View to create a new VPN configuration."""
    model = AmneziaConfig
    form_class = AmneziaConfigForm
    success_url = reverse_lazy('vpn_panel:dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Server profile created successfully.")
        return super().form_valid(form)

class ConfigUpdateView(LoginRequiredMixin, UpdateView):
    """View to update an existing VPN configuration."""
    model = AmneziaConfig
    form_class = AmneziaConfigForm
    success_url = reverse_lazy('vpn_panel:dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Server profile updated successfully.")
        
        # If the updated config is currently active, we might want to restart it,
        # but for safety, we just let the user handle restarting.
        if self.object.is_active:
            messages.warning(self.request, "This profile is currently active. Please disconnect and reconnect to apply changes.")
            
        return super().form_valid(form)

class ConfigDeleteView(LoginRequiredMixin, DeleteView):
    """View to delete a VPN configuration."""
    model = AmneziaConfig
    success_url = reverse_lazy('vpn_panel:dashboard')

    def form_valid(self, form):
        if self.object.is_active:
            VPNManager.stop_connection()
        messages.success(self.request, "Server profile deleted successfully.")
        return super().form_valid(form)

class ToggleConnectionView(LoginRequiredMixin, View):
    """View to start or stop a specific VPN connection."""
    
    def post(self, request, pk):
        action = request.POST.get('action')
        config = get_object_or_404(AmneziaConfig, pk=pk)
        
        if action == 'start':
            # Stop any currently active connection first
            if VPNManager.is_connected():
                VPNManager.stop_connection()
                
            success, msg = VPNManager.start_connection(config.config_content)
            if success:
                config.is_active = True
                config.save()
                messages.success(request, f"Connected to {config.name}.")
            else:
                messages.error(request, f"Failed to connect: {msg}")
                
        elif action == 'stop':
            success, msg = VPNManager.stop_connection()
            if success:
                config.is_active = False
                config.save()
                messages.success(request, "Disconnected successfully.")
            else:
                messages.error(request, f"Failed to disconnect: {msg}")
                
        return redirect('vpn_panel:dashboard')

class PingCheckView(LoginRequiredMixin, View):
    """AJAX view to check latency of a specific configuration."""
    
    def get(self, request, pk):
        config = get_object_or_404(AmneziaConfig, pk=pk)
        latency = PingService.ping(config.endpoint_ip)
        
        # Save latency for future display
        config.last_latency = latency
        config.save(update_fields=['last_latency'])
        
        return JsonResponse({'latency': latency})

class LogsView(LoginRequiredMixin, View):
    """View to display system and VPN logs."""
    
    def get(self, request):
        sys_logs = LogService.get_system_logs(200)
        vpn_logs = LogService.get_vpn_logs(200)
        return render(request, 'vpn_panel/logs.html', {
            'sys_logs': sys_logs,
            'vpn_logs': vpn_logs,
            'is_system_connected': VPNManager.is_connected()
        })
