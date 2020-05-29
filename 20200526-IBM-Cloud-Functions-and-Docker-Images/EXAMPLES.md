Using a docker image for a cloud function
```
% ic fn action create calculate_alignment calculate_alignment.py --docker hammertoe/librosa_ml:latest
```

Invoking the function
```
% ic fn action invoke calculate_alignment -p referece leader.wav -p part sarah.wav
```