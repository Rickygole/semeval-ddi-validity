# Coverage of the two-way, one-way drug and partner-only bootstraps

Status: post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision.

Simulation on the real (label, drug, partner) structure. 1000 replicates per scenario and design, 1000 bootstrap draws per replicate, seed 7. Score = beta_d y + sigma_p u_partner + v_drug + e, beta_d = beta + tau z_d; the true within-drug AUROC is Phi(beta / sqrt(2 (sigma_p^2 + 1) + tau^2)). Ratio = mean 90% half-width / (1.645 x replicate SD); 1 is calibrated. Labels: calibrated if 90% coverage is in [0.87, 0.93] and the ratio in [0.85, 1.15]; anti-conservative if coverage is below 0.87; otherwise conservative.

| design | true AUROC | sigma_p | tau | SD | bootstrap | coverage 90% | coverage 95% | 90% half-width | ratio | 90% inside 0.40 to 0.60 | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| older_clean tier A | 0.450 | 0.0 | 0.0 | 0.017 | two_way | 0.997 | 0.999 | 0.052 | 1.847 | 0.467 | conservative |
| older_clean tier A | 0.450 | 0.0 | 0.0 | 0.017 | one_way_drug | 0.890 | 0.942 | 0.027 | 0.974 | 0.917 | calibrated |
| older_clean tier A | 0.450 | 0.0 | 0.0 | 0.017 | partner_only | 0.923 | 0.969 | 0.031 | 1.119 | 0.872 | calibrated |
| older_clean tier A | 0.450 | 0.0 | 0.5 | 0.023 | two_way | 0.991 | 0.996 | 0.057 | 1.546 | 0.372 | conservative |
| older_clean tier A | 0.450 | 0.0 | 0.5 | 0.023 | one_way_drug | 0.871 | 0.941 | 0.035 | 0.953 | 0.739 | calibrated |
| older_clean tier A | 0.450 | 0.0 | 0.5 | 0.023 | partner_only | 0.828 | 0.902 | 0.032 | 0.868 | 0.786 | anti-conservative |
| older_clean tier A | 0.450 | 1.0 | 0.0 | 0.014 | two_way | 1.000 | 1.000 | 0.050 | 2.186 | 0.518 | conservative |
| older_clean tier A | 0.450 | 1.0 | 0.0 | 0.014 | one_way_drug | 0.951 | 0.985 | 0.027 | 1.207 | 0.957 | conservative |
| older_clean tier A | 0.450 | 1.0 | 0.0 | 0.014 | partner_only | 0.954 | 0.987 | 0.027 | 1.201 | 0.955 | conservative |
| older_clean tier A | 0.450 | 1.0 | 0.5 | 0.017 | two_way | 0.997 | 1.000 | 0.053 | 1.895 | 0.449 | conservative |
| older_clean tier A | 0.450 | 1.0 | 0.5 | 0.017 | one_way_drug | 0.943 | 0.966 | 0.032 | 1.149 | 0.857 | conservative |
| older_clean tier A | 0.450 | 1.0 | 0.5 | 0.017 | partner_only | 0.913 | 0.945 | 0.028 | 1.004 | 0.911 | calibrated |
| older_clean tier A | 0.500 | 0.0 | 0.0 | 0.017 | two_way | 0.995 | 0.998 | 0.052 | 1.826 | 0.994 | conservative |
| older_clean tier A | 0.500 | 0.0 | 0.0 | 0.017 | one_way_drug | 0.882 | 0.937 | 0.028 | 0.966 | 1.000 | calibrated |
| older_clean tier A | 0.500 | 0.0 | 0.0 | 0.017 | partner_only | 0.923 | 0.967 | 0.031 | 1.100 | 1.000 | calibrated |
| older_clean tier A | 0.500 | 0.0 | 0.5 | 0.022 | two_way | 0.992 | 0.999 | 0.058 | 1.615 | 0.948 | conservative |
| older_clean tier A | 0.500 | 0.0 | 0.5 | 0.022 | one_way_drug | 0.896 | 0.948 | 0.036 | 0.999 | 0.999 | calibrated |
| older_clean tier A | 0.500 | 0.0 | 0.5 | 0.022 | partner_only | 0.858 | 0.919 | 0.032 | 0.904 | 0.999 | anti-conservative |
| older_clean tier A | 0.500 | 1.0 | 0.0 | 0.014 | two_way | 1.000 | 1.000 | 0.050 | 2.131 | 1.000 | conservative |
| older_clean tier A | 0.500 | 1.0 | 0.0 | 0.014 | one_way_drug | 0.958 | 0.986 | 0.028 | 1.183 | 1.000 | conservative |
| older_clean tier A | 0.500 | 1.0 | 0.0 | 0.014 | partner_only | 0.958 | 0.983 | 0.027 | 1.163 | 1.000 | conservative |
| older_clean tier A | 0.500 | 1.0 | 0.5 | 0.018 | two_way | 0.996 | 1.000 | 0.053 | 1.783 | 0.987 | conservative |
| older_clean tier A | 0.500 | 1.0 | 0.5 | 0.018 | one_way_drug | 0.923 | 0.965 | 0.032 | 1.084 | 1.000 | calibrated |
| older_clean tier A | 0.500 | 1.0 | 0.5 | 0.018 | partner_only | 0.866 | 0.928 | 0.028 | 0.942 | 1.000 | anti-conservative |
| older_clean tier A | 0.600 | 0.0 | 0.0 | 0.017 | two_way | 0.999 | 1.000 | 0.051 | 1.855 | 0.000 | conservative |
| older_clean tier A | 0.600 | 0.0 | 0.0 | 0.017 | one_way_drug | 0.897 | 0.946 | 0.027 | 0.976 | 0.046 | calibrated |
| older_clean tier A | 0.600 | 0.0 | 0.0 | 0.017 | partner_only | 0.936 | 0.977 | 0.031 | 1.121 | 0.032 | conservative |
| older_clean tier A | 0.600 | 0.0 | 0.5 | 0.021 | two_way | 0.989 | 0.997 | 0.056 | 1.627 | 0.005 | conservative |
| older_clean tier A | 0.600 | 0.0 | 0.5 | 0.021 | one_way_drug | 0.907 | 0.949 | 0.035 | 1.000 | 0.052 | calibrated |
| older_clean tier A | 0.600 | 0.0 | 0.5 | 0.021 | partner_only | 0.872 | 0.933 | 0.032 | 0.912 | 0.067 | calibrated |
| older_clean tier A | 0.600 | 1.0 | 0.0 | 0.014 | two_way | 0.999 | 0.999 | 0.049 | 2.107 | 0.001 | conservative |
| older_clean tier A | 0.600 | 1.0 | 0.0 | 0.014 | one_way_drug | 0.929 | 0.975 | 0.027 | 1.153 | 0.028 | conservative |
| older_clean tier A | 0.600 | 1.0 | 0.0 | 0.014 | partner_only | 0.941 | 0.977 | 0.027 | 1.178 | 0.024 | conservative |
| older_clean tier A | 0.600 | 1.0 | 0.5 | 0.018 | two_way | 0.994 | 1.000 | 0.052 | 1.743 | 0.001 | conservative |
| older_clean tier A | 0.600 | 1.0 | 0.5 | 0.018 | one_way_drug | 0.917 | 0.956 | 0.031 | 1.044 | 0.039 | calibrated |
| older_clean tier A | 0.600 | 1.0 | 0.5 | 0.018 | partner_only | 0.874 | 0.933 | 0.028 | 0.937 | 0.063 | calibrated |
| older_clean tier B | 0.450 | 0.0 | 0.0 | 0.026 | two_way | 0.998 | 1.000 | 0.080 | 1.885 | 0.110 | conservative |
| older_clean tier B | 0.450 | 0.0 | 0.0 | 0.026 | one_way_drug | 0.892 | 0.940 | 0.041 | 0.967 | 0.628 | calibrated |
| older_clean tier B | 0.450 | 0.0 | 0.0 | 0.026 | partner_only | 0.942 | 0.973 | 0.049 | 1.158 | 0.514 | conservative |
| older_clean tier B | 0.450 | 0.0 | 0.5 | 0.030 | two_way | 0.995 | 0.999 | 0.086 | 1.736 | 0.095 | conservative |
| older_clean tier B | 0.450 | 0.0 | 0.5 | 0.030 | one_way_drug | 0.887 | 0.958 | 0.050 | 1.004 | 0.500 | calibrated |
| older_clean tier B | 0.450 | 0.0 | 0.5 | 0.030 | partner_only | 0.904 | 0.959 | 0.051 | 1.018 | 0.484 | calibrated |
| older_clean tier B | 0.450 | 1.0 | 0.0 | 0.026 | two_way | 0.998 | 1.000 | 0.081 | 1.902 | 0.110 | conservative |
| older_clean tier B | 0.450 | 1.0 | 0.0 | 0.026 | one_way_drug | 0.893 | 0.937 | 0.041 | 0.974 | 0.616 | calibrated |
| older_clean tier B | 0.450 | 1.0 | 0.0 | 0.026 | partner_only | 0.948 | 0.979 | 0.050 | 1.184 | 0.478 | conservative |
| older_clean tier B | 0.450 | 1.0 | 0.5 | 0.029 | two_way | 0.996 | 0.999 | 0.084 | 1.769 | 0.110 | conservative |
| older_clean tier B | 0.450 | 1.0 | 0.5 | 0.029 | one_way_drug | 0.891 | 0.935 | 0.046 | 0.970 | 0.566 | calibrated |
| older_clean tier B | 0.450 | 1.0 | 0.5 | 0.029 | partner_only | 0.917 | 0.959 | 0.051 | 1.071 | 0.499 | calibrated |
| older_clean tier B | 0.500 | 0.0 | 0.0 | 0.025 | two_way | 1.000 | 1.000 | 0.081 | 1.943 | 0.524 | conservative |
| older_clean tier B | 0.500 | 0.0 | 0.0 | 0.025 | one_way_drug | 0.893 | 0.948 | 0.042 | 0.998 | 0.981 | calibrated |
| older_clean tier B | 0.500 | 0.0 | 0.0 | 0.025 | partner_only | 0.944 | 0.982 | 0.050 | 1.197 | 0.956 | conservative |
| older_clean tier B | 0.500 | 0.0 | 0.5 | 0.033 | two_way | 0.995 | 0.999 | 0.087 | 1.614 | 0.295 | conservative |
| older_clean tier B | 0.500 | 0.0 | 0.5 | 0.033 | one_way_drug | 0.869 | 0.928 | 0.050 | 0.935 | 0.864 | anti-conservative |
| older_clean tier B | 0.500 | 0.0 | 0.5 | 0.033 | partner_only | 0.873 | 0.934 | 0.051 | 0.947 | 0.862 | calibrated |
| older_clean tier B | 0.500 | 1.0 | 0.0 | 0.026 | two_way | 0.999 | 1.000 | 0.081 | 1.891 | 0.529 | conservative |
| older_clean tier B | 0.500 | 1.0 | 0.0 | 0.026 | one_way_drug | 0.880 | 0.943 | 0.041 | 0.963 | 0.976 | calibrated |
| older_clean tier B | 0.500 | 1.0 | 0.0 | 0.026 | partner_only | 0.947 | 0.981 | 0.051 | 1.178 | 0.948 | conservative |
| older_clean tier B | 0.500 | 1.0 | 0.5 | 0.030 | two_way | 0.995 | 1.000 | 0.085 | 1.707 | 0.379 | conservative |
| older_clean tier B | 0.500 | 1.0 | 0.5 | 0.030 | one_way_drug | 0.865 | 0.935 | 0.046 | 0.933 | 0.922 | anti-conservative |
| older_clean tier B | 0.500 | 1.0 | 0.5 | 0.030 | partner_only | 0.917 | 0.965 | 0.051 | 1.031 | 0.891 | calibrated |
| older_clean tier B | 0.600 | 0.0 | 0.0 | 0.025 | two_way | 0.997 | 1.000 | 0.079 | 1.901 | 0.002 | conservative |
| older_clean tier B | 0.600 | 0.0 | 0.0 | 0.025 | one_way_drug | 0.893 | 0.953 | 0.040 | 0.972 | 0.042 | calibrated |
| older_clean tier B | 0.600 | 0.0 | 0.0 | 0.025 | partner_only | 0.950 | 0.980 | 0.049 | 1.174 | 0.021 | conservative |
| older_clean tier B | 0.600 | 0.0 | 0.5 | 0.029 | two_way | 0.996 | 0.999 | 0.085 | 1.805 | 0.000 | conservative |
| older_clean tier B | 0.600 | 0.0 | 0.5 | 0.029 | one_way_drug | 0.909 | 0.957 | 0.049 | 1.042 | 0.041 | calibrated |
| older_clean tier B | 0.600 | 0.0 | 0.5 | 0.029 | partner_only | 0.910 | 0.958 | 0.050 | 1.064 | 0.042 | calibrated |
| older_clean tier B | 0.600 | 1.0 | 0.0 | 0.026 | two_way | 0.999 | 1.000 | 0.080 | 1.852 | 0.000 | conservative |
| older_clean tier B | 0.600 | 1.0 | 0.0 | 0.026 | one_way_drug | 0.873 | 0.933 | 0.041 | 0.939 | 0.061 | calibrated |
| older_clean tier B | 0.600 | 1.0 | 0.0 | 0.026 | partner_only | 0.946 | 0.975 | 0.050 | 1.159 | 0.024 | conservative |
| older_clean tier B | 0.600 | 1.0 | 0.5 | 0.028 | two_way | 0.996 | 0.999 | 0.083 | 1.809 | 0.001 | conservative |
| older_clean tier B | 0.600 | 1.0 | 0.5 | 0.028 | one_way_drug | 0.892 | 0.939 | 0.045 | 0.986 | 0.049 | calibrated |
| older_clean tier B | 0.600 | 1.0 | 0.5 | 0.028 | partner_only | 0.926 | 0.967 | 0.050 | 1.100 | 0.030 | calibrated |
| novel tier A | 0.450 | 0.0 | 0.0 | 0.037 | two_way | 0.997 | 1.000 | 0.113 | 1.869 | 0.000 | conservative |
| novel tier A | 0.450 | 0.0 | 0.0 | 0.037 | one_way_drug | 0.881 | 0.936 | 0.057 | 0.955 | 0.395 | calibrated |
| novel tier A | 0.450 | 0.0 | 0.0 | 0.037 | partner_only | 0.935 | 0.970 | 0.070 | 1.161 | 0.257 | conservative |
| novel tier A | 0.450 | 0.0 | 0.5 | 0.043 | two_way | 0.995 | 1.000 | 0.119 | 1.692 | 0.000 | conservative |
| novel tier A | 0.450 | 0.0 | 0.5 | 0.043 | one_way_drug | 0.872 | 0.929 | 0.067 | 0.948 | 0.315 | calibrated |
| novel tier A | 0.450 | 0.0 | 0.5 | 0.043 | partner_only | 0.897 | 0.944 | 0.072 | 1.019 | 0.257 | calibrated |
| novel tier A | 0.450 | 1.0 | 0.0 | 0.030 | two_way | 1.000 | 1.000 | 0.108 | 2.228 | 0.001 | conservative |
| novel tier A | 0.450 | 1.0 | 0.0 | 0.030 | one_way_drug | 0.951 | 0.978 | 0.058 | 1.185 | 0.389 | conservative |
| novel tier A | 0.450 | 1.0 | 0.0 | 0.030 | partner_only | 0.963 | 0.987 | 0.062 | 1.284 | 0.335 | conservative |
| novel tier A | 0.450 | 1.0 | 0.5 | 0.034 | two_way | 1.000 | 1.000 | 0.112 | 1.979 | 0.001 | conservative |
| novel tier A | 0.450 | 1.0 | 0.5 | 0.034 | one_way_drug | 0.925 | 0.968 | 0.062 | 1.098 | 0.360 | calibrated |
| novel tier A | 0.450 | 1.0 | 0.5 | 0.034 | partner_only | 0.931 | 0.966 | 0.063 | 1.123 | 0.340 | conservative |
| novel tier A | 0.500 | 0.0 | 0.0 | 0.036 | two_way | 0.999 | 1.000 | 0.113 | 1.915 | 0.001 | conservative |
| novel tier A | 0.500 | 0.0 | 0.0 | 0.036 | one_way_drug | 0.881 | 0.935 | 0.057 | 0.974 | 0.755 | calibrated |
| novel tier A | 0.500 | 0.0 | 0.0 | 0.036 | partner_only | 0.942 | 0.981 | 0.070 | 1.191 | 0.587 | conservative |
| novel tier A | 0.500 | 0.0 | 0.5 | 0.041 | two_way | 0.994 | 0.998 | 0.119 | 1.750 | 0.000 | conservative |
| novel tier A | 0.500 | 0.0 | 0.5 | 0.041 | one_way_drug | 0.896 | 0.942 | 0.067 | 0.979 | 0.566 | calibrated |
| novel tier A | 0.500 | 0.0 | 0.5 | 0.041 | partner_only | 0.920 | 0.961 | 0.072 | 1.051 | 0.488 | calibrated |
| novel tier A | 0.500 | 1.0 | 0.0 | 0.030 | two_way | 0.999 | 1.000 | 0.109 | 2.198 | 0.009 | conservative |
| novel tier A | 0.500 | 1.0 | 0.0 | 0.030 | one_way_drug | 0.934 | 0.973 | 0.058 | 1.168 | 0.838 | conservative |
| novel tier A | 0.500 | 1.0 | 0.0 | 0.030 | partner_only | 0.958 | 0.978 | 0.062 | 1.262 | 0.788 | conservative |
| novel tier A | 0.500 | 1.0 | 0.5 | 0.034 | two_way | 1.000 | 1.000 | 0.112 | 2.017 | 0.003 | conservative |
| novel tier A | 0.500 | 1.0 | 0.5 | 0.034 | one_way_drug | 0.928 | 0.959 | 0.063 | 1.134 | 0.722 | calibrated |
| novel tier A | 0.500 | 1.0 | 0.5 | 0.034 | partner_only | 0.932 | 0.964 | 0.064 | 1.143 | 0.712 | conservative |
| novel tier A | 0.600 | 0.0 | 0.0 | 0.035 | two_way | 0.998 | 1.000 | 0.111 | 1.923 | 0.000 | conservative |
| novel tier A | 0.600 | 0.0 | 0.0 | 0.035 | one_way_drug | 0.890 | 0.943 | 0.057 | 0.983 | 0.049 | calibrated |
| novel tier A | 0.600 | 0.0 | 0.0 | 0.035 | partner_only | 0.951 | 0.978 | 0.069 | 1.197 | 0.027 | conservative |
| novel tier A | 0.600 | 0.0 | 0.5 | 0.039 | two_way | 0.998 | 0.998 | 0.117 | 1.828 | 0.000 | conservative |
| novel tier A | 0.600 | 0.0 | 0.5 | 0.039 | one_way_drug | 0.902 | 0.949 | 0.065 | 1.023 | 0.038 | calibrated |
| novel tier A | 0.600 | 0.0 | 0.5 | 0.039 | partner_only | 0.925 | 0.968 | 0.070 | 1.096 | 0.034 | calibrated |
| novel tier A | 0.600 | 1.0 | 0.0 | 0.030 | two_way | 0.999 | 1.000 | 0.107 | 2.126 | 0.000 | conservative |
| novel tier A | 0.600 | 1.0 | 0.0 | 0.030 | one_way_drug | 0.930 | 0.963 | 0.056 | 1.126 | 0.037 | calibrated |
| novel tier A | 0.600 | 1.0 | 0.0 | 0.030 | partner_only | 0.946 | 0.981 | 0.061 | 1.226 | 0.026 | conservative |
| novel tier A | 0.600 | 1.0 | 0.5 | 0.035 | two_way | 0.997 | 0.999 | 0.110 | 1.914 | 0.000 | conservative |
| novel tier A | 0.600 | 1.0 | 0.5 | 0.035 | one_way_drug | 0.909 | 0.953 | 0.061 | 1.063 | 0.043 | calibrated |
| novel tier A | 0.600 | 1.0 | 0.5 | 0.035 | partner_only | 0.918 | 0.965 | 0.063 | 1.093 | 0.042 | calibrated |
| novel tier B | 0.450 | 0.0 | 0.0 | 0.046 | two_way | 0.999 | 1.000 | 0.149 | 1.955 | 0.000 | conservative |
| novel tier B | 0.450 | 0.0 | 0.0 | 0.046 | one_way_drug | 0.887 | 0.933 | 0.075 | 0.976 | 0.259 | calibrated |
| novel tier B | 0.450 | 0.0 | 0.0 | 0.046 | partner_only | 0.949 | 0.975 | 0.095 | 1.243 | 0.061 | conservative |
| novel tier B | 0.450 | 0.0 | 0.5 | 0.053 | two_way | 0.995 | 0.998 | 0.156 | 1.802 | 0.000 | conservative |
| novel tier B | 0.450 | 0.0 | 0.5 | 0.053 | one_way_drug | 0.891 | 0.936 | 0.084 | 0.968 | 0.153 | calibrated |
| novel tier B | 0.450 | 0.0 | 0.5 | 0.053 | partner_only | 0.926 | 0.969 | 0.097 | 1.116 | 0.040 | calibrated |
| novel tier B | 0.450 | 1.0 | 0.0 | 0.046 | two_way | 0.998 | 1.000 | 0.148 | 1.959 | 0.000 | conservative |
| novel tier B | 0.450 | 1.0 | 0.0 | 0.046 | one_way_drug | 0.886 | 0.943 | 0.074 | 0.986 | 0.245 | calibrated |
| novel tier B | 0.450 | 1.0 | 0.0 | 0.046 | partner_only | 0.952 | 0.978 | 0.092 | 1.225 | 0.058 | conservative |
| novel tier B | 0.450 | 1.0 | 0.5 | 0.050 | two_way | 0.997 | 0.999 | 0.152 | 1.862 | 0.000 | conservative |
| novel tier B | 0.450 | 1.0 | 0.5 | 0.050 | one_way_drug | 0.897 | 0.943 | 0.080 | 0.977 | 0.206 | calibrated |
| novel tier B | 0.450 | 1.0 | 0.5 | 0.050 | partner_only | 0.940 | 0.968 | 0.094 | 1.150 | 0.067 | conservative |
| novel tier B | 0.500 | 0.0 | 0.0 | 0.047 | two_way | 0.997 | 0.999 | 0.151 | 1.953 | 0.000 | conservative |
| novel tier B | 0.500 | 0.0 | 0.0 | 0.047 | one_way_drug | 0.900 | 0.943 | 0.075 | 0.968 | 0.388 | calibrated |
| novel tier B | 0.500 | 0.0 | 0.0 | 0.047 | partner_only | 0.958 | 0.986 | 0.096 | 1.242 | 0.088 | conservative |
| novel tier B | 0.500 | 0.0 | 0.5 | 0.054 | two_way | 0.998 | 0.999 | 0.157 | 1.766 | 0.000 | conservative |
| novel tier B | 0.500 | 0.0 | 0.5 | 0.054 | one_way_drug | 0.877 | 0.935 | 0.084 | 0.947 | 0.229 | calibrated |
| novel tier B | 0.500 | 0.0 | 0.5 | 0.054 | partner_only | 0.918 | 0.967 | 0.097 | 1.096 | 0.058 | calibrated |
| novel tier B | 0.500 | 1.0 | 0.0 | 0.047 | two_way | 0.998 | 1.000 | 0.149 | 1.912 | 0.000 | conservative |
| novel tier B | 0.500 | 1.0 | 0.0 | 0.047 | one_way_drug | 0.876 | 0.941 | 0.075 | 0.967 | 0.383 | calibrated |
| novel tier B | 0.500 | 1.0 | 0.0 | 0.047 | partner_only | 0.954 | 0.982 | 0.093 | 1.197 | 0.125 | conservative |
| novel tier B | 0.500 | 1.0 | 0.5 | 0.048 | two_way | 0.999 | 1.000 | 0.152 | 1.909 | 0.000 | conservative |
| novel tier B | 0.500 | 1.0 | 0.5 | 0.048 | one_way_drug | 0.893 | 0.943 | 0.079 | 0.997 | 0.340 | calibrated |
| novel tier B | 0.500 | 1.0 | 0.5 | 0.048 | partner_only | 0.944 | 0.974 | 0.094 | 1.182 | 0.097 | conservative |
| novel tier B | 0.600 | 0.0 | 0.0 | 0.046 | two_way | 0.999 | 1.000 | 0.147 | 1.924 | 0.000 | conservative |
| novel tier B | 0.600 | 0.0 | 0.0 | 0.046 | one_way_drug | 0.883 | 0.931 | 0.073 | 0.956 | 0.052 | calibrated |
| novel tier B | 0.600 | 0.0 | 0.0 | 0.046 | partner_only | 0.950 | 0.985 | 0.094 | 1.227 | 0.013 | conservative |
| novel tier B | 0.600 | 0.0 | 0.5 | 0.053 | two_way | 0.997 | 1.000 | 0.153 | 1.770 | 0.000 | conservative |
| novel tier B | 0.600 | 0.0 | 0.5 | 0.053 | one_way_drug | 0.870 | 0.918 | 0.083 | 0.953 | 0.036 | calibrated |
| novel tier B | 0.600 | 0.0 | 0.5 | 0.053 | partner_only | 0.918 | 0.963 | 0.095 | 1.098 | 0.013 | calibrated |
| novel tier B | 0.600 | 1.0 | 0.0 | 0.045 | two_way | 0.999 | 1.000 | 0.146 | 1.964 | 0.000 | conservative |
| novel tier B | 0.600 | 1.0 | 0.0 | 0.045 | one_way_drug | 0.892 | 0.939 | 0.073 | 0.985 | 0.047 | calibrated |
| novel tier B | 0.600 | 1.0 | 0.0 | 0.045 | partner_only | 0.951 | 0.982 | 0.092 | 1.236 | 0.017 | conservative |
| novel tier B | 0.600 | 1.0 | 0.5 | 0.049 | two_way | 0.997 | 1.000 | 0.149 | 1.852 | 0.000 | conservative |
| novel tier B | 0.600 | 1.0 | 0.5 | 0.049 | one_way_drug | 0.877 | 0.936 | 0.078 | 0.972 | 0.050 | calibrated |
| novel tier B | 0.600 | 1.0 | 0.5 | 0.049 | partner_only | 0.931 | 0.977 | 0.093 | 1.153 | 0.018 | conservative |

## Summary by design and bootstrap

| design | bootstrap | coverage 90% range | ratio range | labels | adequate (no anti-conservative scenario) |
| --- | --- | --- | --- | --- | --- |
| older_clean tier A | two_way | [0.989, 1.000] | [1.546, 2.186] | conservative | True |
| older_clean tier A | one_way_drug | [0.871, 0.958] | [0.953, 1.207] | calibrated, conservative | True |
| older_clean tier A | partner_only | [0.828, 0.958] | [0.868, 1.201] | anti-conservative, calibrated, conservative | False |
| older_clean tier B | two_way | [0.995, 1.000] | [1.614, 1.943] | conservative | True |
| older_clean tier B | one_way_drug | [0.865, 0.909] | [0.933, 1.042] | anti-conservative, calibrated | False |
| older_clean tier B | partner_only | [0.873, 0.950] | [0.947, 1.197] | calibrated, conservative | True |
| novel tier A | two_way | [0.994, 1.000] | [1.692, 2.228] | conservative | True |
| novel tier A | one_way_drug | [0.872, 0.951] | [0.948, 1.185] | calibrated, conservative | True |
| novel tier A | partner_only | [0.897, 0.963] | [1.019, 1.284] | calibrated, conservative | True |
| novel tier B | two_way | [0.995, 0.999] | [1.766, 1.964] | conservative | True |
| novel tier B | one_way_drug | [0.870, 0.900] | [0.947, 0.997] | calibrated | True |
| novel tier B | partner_only | [0.918, 0.958] | [1.096, 1.243] | calibrated, conservative | True |
