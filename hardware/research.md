# QC35 feasibility research

Checked 20 September 2026. Sources establish starting points; they do not validate the proposed combined modification.

## Evidence

- [James Turton’s QC35 USB-C project](https://github.com/jamesturton/bose-qc35-usb-c) provides KiCad sources and fabrication files for a replacement daughterboard. Its author reports compatibility with QC35 I and II and preservation of charging/firmware USB functions. Fine-pitch assembly and housing modification are required. This is a connector-board precedent, not evidence that extra compute can be powered or charged safely through it. Inspect the upstream licence before copying design files.
- [Bose QC35 wired-connection guidance](https://www.bose.co.nz/en_nz/support/articles/HC756/productCodes/qc35/article.html) says the 2.5 mm audio cable disables Bluetooth. Therefore a permanently connected AUX source does not meet the desired normal Bluetooth/call behaviour. Internal injection and call priority remain unproven. Test individual buttons rather than assuming all controls behave alike in wired mode.
- [iFixit partial teardown](https://www.ifixit.com/Teardown/Bose+QuietComfort+35+PARTIAL+Teardown/114932) shows multiple boards, delicate cables and battery connections. It is a contributor teardown, not an official service schematic; its battery capacity estimate is not a confirmed specification for this particular headset. Free volume, acoustic effects and thermal margin must be measured.

## Compute candidates, not purchase recommendations

| Candidate | Documented basis | Missing evidence |
| --- | --- | --- |
| ESP32-S3 module | [Espressif datasheet](https://documentation.espressif.com/esp32-s3-wroom-2_datasheet_en.html): Wi-Fi, BLE, I²S and storage interfaces | Actual decoder support, usable memory/storage, measured playback/sync power, DAC design, maintainable firmware and required binary components. BLE is not conventional Bluetooth audio. |
| Linux prototype | [Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/): 65 × 30 mm, Wi-Fi/Bluetooth, microSD and Linux-capable compute | Earcup fit, idle/playback power, heat, boot latency and firmware openness. Useful benchmark platform, not selected internal hardware. |

Select the module using measured runtime, fit, heat, codec compatibility, openness and maintenance effort. Do not assume “mini-computer” requires Linux or that an MCU automatically meets the audio requirements.

## Bench questions

1. Identify QC35 generation, board revision and firmware; record unmodified ANC, wired audio, Bluetooth, calls and button behaviour.
2. Measure space without compromising drivers, microphone ports, seals, antenna placement or cable movement.
3. Map the audio source-selection path. Determine whether an additional source can coexist with Bose Bluetooth at all, and how an incoming call is detected.
4. Measure noise, volume range and channel balance; avoid assuming analogue injection bypasses every internal conversion.
5. Review one- versus two-cell power architecture, protection, temperature sensing, USB-C input current and charging while operating. Do not parallel charger outputs or batteries by assumption.
6. USB data needs its own topology: retaining Bose firmware data and adding computer USB cannot be achieved by simply wiring both devices to the same data pair.
7. Characterise playback, BLE control, sync and sleep power, then calculate runtime from measured usable battery energy.

Use an external prototype before earcup integration. Preserve the original boards and document changes so the design remains serviceable and reproducible.
