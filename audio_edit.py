import hashlib
import os
from datetime import datetime

import numpy as np
from pedalboard.io import AudioFile


async def bolaklarga_ajrat_va_saqlash(input_file, threshold=0.00005):
    with AudioFile(input_file) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate
        num_channels = f.num_channels

    audio = audio[0]
    extracted_segments = []
    if len(audio) <= 200000:
        extracted_segments.append(audio)
        os.remove(input_file)
    else:
        for i in range(80000, 160000):
            if audio[i] <= threshold:
                extracted_segments.append(audio[:i])

                if len(audio.shape) == 1:
                    new_audio = np.concatenate((audio[:0 * samplerate], audio[i:]))
                    new_audio = new_audio.reshape(1, -1)
                else:
                    new_audio = np.concatenate((audio[:, :0 * samplerate], audio[:, i:]), axis=1)

                with AudioFile(input_file, 'w', samplerate=samplerate, num_channels=num_channels) as f:
                    f.write(new_audio)

                break

    final_audio = np.concatenate(extracted_segments) if extracted_segments else np.array([])

    if final_audio.size > 0:
        now = datetime.now()

        microseconds = now.microsecond
        output_file = hashlib.sha256(str(microseconds).encode()).hexdigest()
        file = f"edited_audios/{output_file}.WAV"
        with AudioFile(file, "w", samplerate, num_channels=1) as f:
            f.write(final_audio)
            return file
        # print(f"Kesilgan audio saqlandi: {output_file}")
    # else:
    #     print("Kesilgan qismlar topilmadi yoki fayl bo'sh.")

# input_audio = "qwerty.WAV"
# output_audio = "extracted_segments3.wav"
# bolaklarga_ajrat_va_saqlash(input_audio, output_audio)
