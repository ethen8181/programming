class PIDController:
    """
    
    for i in range(control_rounds):
        pid_controller.update(metric_value, previous_metric_value, reference_point)
        phi = pid_controller.phi_
        
        
        batch_start = i * batch_size
        batch_end = (i + 1) * batch_size
        for j in range(batch_start, batch_end):
            // compute the update
        
        
        previous_metric_value = metric_value
        
        // compute the new metric_value
        ecpc = total_cost / total_clicks
        win_rate = total_wins / batch_end
        
        if target_metric == 'ecpc':
            metric_value = ecpc
        elif target_metric == 'win_rate':
            metric_value = win_rate
    """

    def __init__(self, param_p, param_i, param_d, min_phi = -2, max_phi = 5):
        self.param_p = param_p
        self.param_i = param_i
        self.param_d = param_d
        self.min_phi = min_phi
        self.max_phi = max_phi

        self.iteration_ = 0
        self.error_sum_ = 0.0
        self.phi_ = 0

    def update(self, metric_value, previous_metric_value, reference_point):
        if self.iteration_ == 0:
            self.phi_ = 0.0
        else:
            error = reference_point - metric_value
            self.error_sum_ += error
            phi = self.param_p * error + self.param_i * self.error_sum_
            if self.iteration_ > 1:
                phi += self.param_d * (previous_metric_value - metric_value)

            phi = max(phi, self.min_phi)
            phi = min(phi, self.max_phi)
            self.phi_ = phi

        self.iteration_ += 1
        return self