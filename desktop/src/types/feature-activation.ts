export interface FeatureActivation {
  featureName: string;
  available: boolean;
  lastCheckedAt: string;
  detail?: string | null;
}

export interface FeatureActivationResult<T> {
  activation: FeatureActivation;
  data?: T;
}

