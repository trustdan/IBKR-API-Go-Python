// ReloadConfig reloads the scanner service configuration
func (s *ScannerService) ReloadConfig() error {
	// Attempt to reload configuration from the same path
	newConfig, err := LoadConfig(s.configPath)
	if err != nil {
		return err
	}

	// Update service configuration
	s.mu.Lock()
	defer s.mu.Unlock()

	// Apply changes
	s.config = newConfig
	logrus.Infof("Reloaded configuration: MaxConcurrency=%d, CacheTTL=%d",
		s.config.MaxConcurrency, s.config.CacheTTL)

	// Update worker pool configuration if needed
	if s.pool != nil {
		s.pool.SetMaxConcurrency(s.config.MaxConcurrency)
	}

	return nil
}
