---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>

# 👋 About Me
I am a Ph.D. student in Artificial Intelligence at Beihang University (BUAA), advised by Prof. [Bo Li](https://iai.buaa.edu.cn/info/1013/1089.htm) and Prof. [Xingxing Wei](https://sites.google.com/site/xingxingwei1988/). My research interests include **multimodal learning**, **visible-infrared perception**, **remote sensing**, and **MLLM grounding and reasoning**.

My work focuses on multimodal perception and understanding for real-world vision systems, especially RGB-infrared learning, cross-spectral fusion, and robust visual grounding under challenging environments. I am open to academic collaborations, research discussions, internships, and full-time opportunities in related areas.
<i style="color: red; display: inline;"><b>Please feel free to contact me by email for potential collaboration, internship, or professional opportunities.</b></i>

# 🔥 News

- *2026.06*: &nbsp;🎉🎉 One paper was accepted to ECCV 2026 (RGBT-GroundBench).
- *2026.02*: &nbsp;🎉🎉 One paper was accepted to CVPR 2026 (NS-FPN).
- *2026.01*: &nbsp; My personal website went live.
- *2025.12*: &nbsp;🎉🎉 One paper was accepted to IEEE T-ITS (RSDet).
- *2025.07*: &nbsp;🎉🎉 One paper was accepted to Journal of Computer-Aided Design and Computer Graphics.
- *2025.07*: &nbsp;🎉🎉 One paper was accepted to ACM MM 2025 (UniRGB-IR).
- *2025.06*: &nbsp;🎉🎉 One paper was accepted to ICCV 2025 (M2D-LIF).

# 📝 Publications

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ECCV 2026</div><img src='images/500x300.png' alt="RGBT-GroundBench placeholder" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[RGBT-GroundBench: Visual Grounding Beyond RGB in Complex Real-World Scenarios](https://arxiv.org/abs/2512.24561)

**Tianyi Zhao**, Jiawen Xi, Linhui Xiao, Junnan Li, Xue Yang, Maoxun Yuan, Xingxing Wei

[**Paper**](https://arxiv.org/abs/2512.24561) / [**Code**](https://github.com/crazyxiaoxi/RGBTVG) / [**Dataset**](https://huggingface.co/datasets/JiawenXi/RGBT-Ground-Dataset) / [**Models**](https://huggingface.co/JiawenXi/RGBT-Ground-Model)
- We present RGBT-GroundBench, the first large-scale benchmark for RGB-Thermal visual grounding in complex real-world scenarios. It provides over 40K images, 21,535 RGB-TIR pairs, and 38,760 object instances with referring expressions, bounding boxes, and fine-grained annotations for scenes, environmental conditions, and object properties. We also introduce a unified evaluation protocol for RGB-only, TIR-only, and RGB+TIR inputs, benchmark 11 representative grounding models, and provide RGBT-VGNet as a reproducible baseline for reliable cross-spectral grounding.
</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ICCV 2025</div><img src='images/500x300.png' alt="M2D-LIF placeholder" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[Rethinking Multi-modal Object Detection from the Perspective of Mono-Modality Feature Learning](https://openaccess.thecvf.com/content/ICCV2025/papers/Zhao_Rethinking_Multi-modal_Object_Detection_from_the_Perspective_of_Mono-Modality_Feature_ICCV_2025_paper.pdf)

**Tianyi Zhao**, Boyang Liu, Yanglei Gao, Yiming Sun, Maoxun Yuan, Xingxing Wei

[**Project**](https://github.com/Zhao-Tian-yi/M2D-LIF) <strong><span class='show_paper_citations' data='mJlOsyYAAAAJ:9yKSN-GCB0IC'></span></strong>
- This work revisits RGB-infrared object detection from the perspective of mono-modality feature learning and shows that strong single-modality representation is a key prerequisite for robust multimodal performance. Based on this insight, we design an improved feature learning and fusion strategy that enhances cross-modal complementarity and detection stability under challenging illumination and occlusion.
</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">TITS 2025</div><img src='images/500x300.png' alt="RSDet placeholder" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[Removal then Selection: A Coarse-to-Fine Fusion Perspective for RGB-Infrared Object Detection](https://ieeexplore.ieee.org/document/11278552)

**Tianyi Zhao**, Maoxun Yuan, Feng Jiang, Nan Wang, Xingxing Wei

[**Project**](https://github.com/Zhao-Tian-yi/RSDet) <strong><span class='show_paper_citations' data='mJlOsyYAAAAJ:YsMSGLbcyi4C'></span></strong>
- This work formulates RGB-infrared fusion as a coarse-to-fine process of "removal then selection," where noisy or redundant cues are filtered before complementary information is integrated. The framework improves robustness in low-light and cluttered scenes while delivering more precise localization.
</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ACM MM 2025</div><img src='images/500x300.png' alt="UniRGB-IR placeholder" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[UniRGB-IR: A Unified Framework for Visible-Infrared Semantic Tasks via Adapter Tuning](https://dl.acm.org/doi/10.1145/3746027.3754806)

Maoxun Yuan, Bo Cui, **Tianyi Zhao**, Jiayi Wang, Shan Fu, Xue Yang, Xingxing Wei

[**Project**](https://github.com/PoTsui99/UniRGB-IR) <strong><span class='show_paper_citations' data='mJlOsyYAAAAJ:2osOgNQ5qMEC'></span></strong>
- UniRGB-IR introduces a unified adapter-tuning framework that lets one shared visible-infrared backbone support multiple semantic tasks efficiently. With task-aware adapters and consistent multimodal transfer, it reduces task-specific retraining cost while preserving strong cross-task performance.
</div>
</div>

# 🎖 Honors and Awards
- 2026 Beihang Youth May Fourth Medal, Nomination Award.
- 2025 National Scholarship.
- 2023 Beijing Outstanding Graduate.
- 2023 Beijing Merit Student.



# 📖 Education
- *2023.09 - Present*, Ph.D. student in Artificial Intelligence, Institute of Artificial Intelligence, Beihang University.
- *2019.09 - 2023.06*, B.Eng., Institute of Artificial Intelligence, Beihang University.


# 💻 Internship
- Available upon request.
