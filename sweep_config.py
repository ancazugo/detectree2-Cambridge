sweep_config = {
    'method': 'bayes', 
    'metric': {
      'name': 'segm/AP50',
      'goal': 'maximize'   
    },
    'parameters': {
        'backbone_freeze_at':
            {'distribution': 'int_uniform',
            'max': 4,
            'min': 1},
        'base_lr':
            {'distribution': 'uniform',
            'max': 0.025,
            'min': 0.00025},
        'batch_size_per_image':
            {'distribution': 'int_uniform',
            'max': 2048,
            'min': 512},
        'dl_num_workers':
            {'distribution': 'int_uniform',
            'max': 8,
            'min': 1},
        'gamma':
            {'distribution': 'uniform',
            'max': 0.3,
            'min': 0.05},
        'warmup_iters':
            {'distribution': 'int_uniform',
            'max': 200,
            'min': 50},
        'weight_decay':
            {'distribution': 'uniform',
            'max': 0.1,
            'min': 0.001}
    }
}  