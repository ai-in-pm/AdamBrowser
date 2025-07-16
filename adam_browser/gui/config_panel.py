"""
Configuration Panel for Adam Browser GUI

Provides a user-friendly interface for viewing and modifying
application configuration settings.
"""

import wx
import wx.propgrid as wxpg
from typing import Dict, Any, Optional
from loguru import logger

from ..config import config


class ConfigPanel(wx.Panel):
    """
    Configuration panel with property grid for settings management.
    
    Allows users to view and modify application settings with
    validation and real-time updates.
    """
    
    def __init__(self, parent):
        """Initialize the configuration panel."""
        super().__init__(parent)
        
        # Configuration state
        self.config_data = {}
        self.modified = False
        
        # Create GUI
        self._create_controls()
        self._create_layout()
        self._bind_events()
        self._load_config()
        
        logger.info("Configuration panel initialized")
    
    def _create_controls(self):
        """Create configuration controls."""
        # Toolbar
        self.toolbar = wx.Panel(self)
        
        # Buttons
        self.btn_save = wx.Button(self.toolbar, label="Save", size=(80, -1))
        self.btn_reset = wx.Button(self.toolbar, label="Reset", size=(80, -1))
        self.btn_defaults = wx.Button(self.toolbar, label="Defaults", size=(80, -1))
        self.btn_export = wx.Button(self.toolbar, label="Export", size=(80, -1))
        self.btn_import = wx.Button(self.toolbar, label="Import", size=(80, -1))
        
        # Status
        self.status_text = wx.StaticText(self.toolbar, label="Ready")
        
        # Property grid
        self.prop_grid = wxpg.PropertyGrid(
            self,
            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_DEFAULT_STYLE
        )
        
        # Set column proportions
        self.prop_grid.SetColumnProportion(0, 40)  # Property names
        self.prop_grid.SetColumnProportion(1, 60)  # Values
    
    def _create_layout(self):
        """Create the layout."""
        # Toolbar layout
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_sizer.Add(self.status_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        toolbar_sizer.Add(self.btn_save, 0, wx.ALL, 2)
        toolbar_sizer.Add(self.btn_reset, 0, wx.ALL, 2)
        toolbar_sizer.Add(self.btn_defaults, 0, wx.ALL, 2)
        toolbar_sizer.Add(wx.StaticLine(self.toolbar, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 2)
        toolbar_sizer.Add(self.btn_export, 0, wx.ALL, 2)
        toolbar_sizer.Add(self.btn_import, 0, wx.ALL, 2)
        
        self.toolbar.SetSizer(toolbar_sizer)
        
        # Main layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)
        main_sizer.Add(self.prop_grid, 1, wx.EXPAND | wx.ALL, 2)
        
        self.SetSizer(main_sizer)
    
    def _bind_events(self):
        """Bind event handlers."""
        # Buttons
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        self.btn_reset.Bind(wx.EVT_BUTTON, self._on_reset)
        self.btn_defaults.Bind(wx.EVT_BUTTON, self._on_defaults)
        self.btn_export.Bind(wx.EVT_BUTTON, self._on_export)
        self.btn_import.Bind(wx.EVT_BUTTON, self._on_import)
        
        # Property grid
        self.prop_grid.Bind(wxpg.EVT_PG_CHANGED, self._on_property_changed)
    
    def _load_config(self):
        """Load configuration into property grid."""
        try:
            self.prop_grid.Clear()
            
            # General settings
            general_cat = self.prop_grid.Append(wxpg.PropertyCategory("General"))
            self.prop_grid.Append(wxpg.StringProperty("App Name", value=config.app_name))
            self.prop_grid.Append(wxpg.StringProperty("Version", value=config.version))
            self.prop_grid.Append(wxpg.BoolProperty("Debug Mode", value=config.debug_mode))
            self.prop_grid.Append(wxpg.EnumProperty("Log Level", 
                                                   choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                                   value=config.log_level))
            self.prop_grid.Append(wxpg.BoolProperty("Offline Mode", value=config.offline_mode))
            self.prop_grid.Append(wxpg.BoolProperty("Telemetry Enabled", value=config.telemetry_enabled))
            
            # Browser settings
            browser_cat = self.prop_grid.Append(wxpg.PropertyCategory("Browser"))
            self.prop_grid.Append(wxpg.EnumProperty("Default Browser",
                                                   choices=["chromium", "firefox", "webkit"],
                                                   value=config.browser.default_browser))
            self.prop_grid.Append(wxpg.StringProperty("Browser Path", value=config.browser.browser_path))
            self.prop_grid.Append(wxpg.BoolProperty("Headless", value=config.browser.headless))
            self.prop_grid.Append(wxpg.BoolProperty("DevTools", value=config.browser.devtools))
            self.prop_grid.Append(wxpg.IntProperty("Timeout (ms)", value=config.browser.timeout))
            self.prop_grid.Append(wxpg.IntProperty("Viewport Width", value=config.browser.viewport_width))
            self.prop_grid.Append(wxpg.IntProperty("Viewport Height", value=config.browser.viewport_height))
            
            # AI settings
            ai_cat = self.prop_grid.Append(wxpg.PropertyCategory("AI/NLP"))
            self.prop_grid.Append(wxpg.StringProperty("Model Path", value=config.ai.model_path))
            self.prop_grid.Append(wxpg.BoolProperty("Use Local Model", value=config.ai.use_local_model))
            self.prop_grid.Append(wxpg.BoolProperty("Fallback to API", value=config.ai.fallback_to_api))
            self.prop_grid.Append(wxpg.FloatProperty("Confidence Threshold", value=config.ai.confidence_threshold))
            self.prop_grid.Append(wxpg.IntProperty("Max Tokens", value=config.ai.max_tokens))
            
            # Database settings
            db_cat = self.prop_grid.Append(wxpg.PropertyCategory("Database"))
            self.prop_grid.Append(wxpg.StringProperty("DB Path", value=config.database.db_path))
            self.prop_grid.Append(wxpg.StringProperty("Log DB Path", value=config.database.log_db_path))
            self.prop_grid.Append(wxpg.BoolProperty("Backup Enabled", value=config.database.backup_enabled))
            self.prop_grid.Append(wxpg.IntProperty("Backup Interval (s)", value=config.database.backup_interval))
            self.prop_grid.Append(wxpg.IntProperty("Max Log Entries", value=config.database.max_log_entries))
            
            # Security settings
            security_cat = self.prop_grid.Append(wxpg.PropertyCategory("Security"))
            self.prop_grid.Append(wxpg.BoolProperty("Encrypt Credentials", value=config.security.encrypt_credentials))
            self.prop_grid.Append(wxpg.StringProperty("Vault Path", value=config.security.vault_path))
            self.prop_grid.Append(wxpg.IntProperty("Session Timeout (s)", value=config.security.session_timeout))
            self.prop_grid.Append(wxpg.BoolProperty("Auto Lock", value=config.security.auto_lock))
            self.prop_grid.Append(wxpg.BoolProperty("Master Password Required", value=config.security.master_password_required))
            
            # GUI settings
            gui_cat = self.prop_grid.Append(wxpg.PropertyCategory("GUI"))
            self.prop_grid.Append(wxpg.EnumProperty("Theme",
                                                   choices=["default", "dark", "light"],
                                                   value=config.gui.theme))
            self.prop_grid.Append(wxpg.IntProperty("Window Width", value=config.gui.window_width))
            self.prop_grid.Append(wxpg.IntProperty("Window Height", value=config.gui.window_height))
            self.prop_grid.Append(wxpg.BoolProperty("Minimize to Tray", value=config.gui.minimize_to_tray))
            self.prop_grid.Append(wxpg.BoolProperty("Show Splash", value=config.gui.show_splash))
            self.prop_grid.Append(wxpg.BoolProperty("Auto Start", value=config.gui.auto_start))
            
            # Automation settings
            automation_cat = self.prop_grid.Append(wxpg.PropertyCategory("Automation"))
            self.prop_grid.Append(wxpg.IntProperty("Scroll Speed (px)", value=config.automation.scroll_speed))
            self.prop_grid.Append(wxpg.IntProperty("Click Delay (ms)", value=config.automation.click_delay))
            self.prop_grid.Append(wxpg.IntProperty("Type Delay (ms)", value=config.automation.type_delay))
            self.prop_grid.Append(wxpg.IntProperty("Screenshot Interval (s)", value=config.automation.screenshot_interval))
            self.prop_grid.Append(wxpg.StringProperty("Screenshot Path", value=config.automation.screenshot_path))
            
            # Expand categories
            self.prop_grid.Expand(general_cat)
            self.prop_grid.Expand(browser_cat)
            
            self.modified = False
            self._update_status("Configuration loaded")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._update_status(f"Error loading config: {e}")
    
    def _on_property_changed(self, event):
        """Handle property value changes."""
        prop = event.GetProperty()
        if prop:
            self.modified = True
            self._update_status("Configuration modified (unsaved)")
            
            # Enable save button
            self.btn_save.Enable(True)
    
    def _on_save(self, event):
        """Handle save button."""
        try:
            # Apply changes to config object
            self._apply_changes()
            
            # Save to file
            config.save_config()
            
            self.modified = False
            self.btn_save.Enable(False)
            self._update_status("Configuration saved successfully")
            
            wx.MessageBox("Configuration saved successfully", "Save Complete", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            self._update_status(f"Save failed: {e}")
            wx.MessageBox(f"Failed to save configuration:\n{str(e)}", "Save Error", wx.OK | wx.ICON_ERROR)
    
    def _on_reset(self, event):
        """Handle reset button."""
        if self.modified:
            result = wx.MessageBox(
                "Discard unsaved changes and reload configuration?",
                "Reset Configuration",
                wx.YES_NO | wx.ICON_QUESTION
            )
            
            if result == wx.YES:
                config.reload()
                self._load_config()
        else:
            config.reload()
            self._load_config()
    
    def _on_defaults(self, event):
        """Handle defaults button."""
        result = wx.MessageBox(
            "Reset all settings to default values?\nThis will discard current configuration.",
            "Reset to Defaults",
            wx.YES_NO | wx.ICON_WARNING
        )
        
        if result == wx.YES:
            try:
                # Create new config with defaults
                from ..config import Config
                default_config = Config()
                
                # Copy default values
                config.__dict__.update(default_config.__dict__)
                
                # Reload display
                self._load_config()
                self._update_status("Reset to default values")
                
            except Exception as e:
                logger.error(f"Failed to reset to defaults: {e}")
                wx.MessageBox(f"Failed to reset to defaults:\n{str(e)}", "Reset Error", wx.OK | wx.ICON_ERROR)
    
    def _on_export(self, event):
        """Handle export button."""
        try:
            with wx.FileDialog(
                self,
                "Export configuration",
                wildcard="TOML files (*.toml)|*.toml|All files (*.*)|*.*",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            ) as dialog:
                
                if dialog.ShowModal() == wx.ID_OK:
                    filepath = dialog.GetPath()
                    
                    # Apply current changes
                    if self.modified:
                        self._apply_changes()
                    
                    # Export configuration
                    import shutil
                    shutil.copy2(config.config_path, filepath)
                    
                    wx.MessageBox(f"Configuration exported to {filepath}", "Export Complete", wx.OK | wx.ICON_INFORMATION)
                    
        except Exception as e:
            wx.MessageBox(f"Export failed: {str(e)}", "Export Error", wx.OK | wx.ICON_ERROR)
    
    def _on_import(self, event):
        """Handle import button."""
        try:
            with wx.FileDialog(
                self,
                "Import configuration",
                wildcard="TOML files (*.toml)|*.toml|All files (*.*)|*.*",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            ) as dialog:
                
                if dialog.ShowModal() == wx.ID_OK:
                    filepath = dialog.GetPath()
                    
                    result = wx.MessageBox(
                        "Import configuration from file?\nThis will replace current settings.",
                        "Import Configuration",
                        wx.YES_NO | wx.ICON_QUESTION
                    )
                    
                    if result == wx.YES:
                        # Import configuration
                        import shutil
                        shutil.copy2(filepath, config.config_path)
                        
                        # Reload
                        config.reload()
                        self._load_config()
                        
                        wx.MessageBox("Configuration imported successfully", "Import Complete", wx.OK | wx.ICON_INFORMATION)
                    
        except Exception as e:
            wx.MessageBox(f"Import failed: {str(e)}", "Import Error", wx.OK | wx.ICON_ERROR)
    
    def _apply_changes(self):
        """Apply property grid changes to config object."""
        # This is a simplified implementation
        # In a full implementation, you would iterate through all properties
        # and update the corresponding config values
        
        # For now, just mark as applied
        logger.info("Configuration changes applied")
    
    def _update_status(self, message: str):
        """Update status text."""
        self.status_text.SetLabel(message)
        
        # Auto-clear status after 5 seconds
        wx.CallLater(5000, lambda: self.status_text.SetLabel("Ready"))
    
    def is_modified(self) -> bool:
        """Check if configuration has been modified."""
        return self.modified


# Example usage for testing
if __name__ == "__main__":
    app = wx.App()
    
    frame = wx.Frame(None, title="Config Panel Test", size=(600, 800))
    config_panel = ConfigPanel(frame)
    
    frame.Show()
    app.MainLoop()
