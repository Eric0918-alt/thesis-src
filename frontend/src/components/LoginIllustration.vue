<template>
  <div class="login-illustration">
    <svg viewBox="0 0 460 420" xmlns="http://www.w3.org/2000/svg" class="illustration-svg">
      <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0b5ef2" />
          <stop offset="55%" stop-color="#1167f6" />
          <stop offset="100%" stop-color="#003db8" />
        </linearGradient>
        <linearGradient id="screenGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.92" />
          <stop offset="55%" stop-color="#38bdf8" stop-opacity="0.72" />
          <stop offset="100%" stop-color="#2563eb" stop-opacity="0.88" />
        </linearGradient>
        <linearGradient id="glowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#67e8f9" stop-opacity="0.65" />
          <stop offset="100%" stop-color="#1d4ed8" stop-opacity="0" />
        </linearGradient>
      </defs>

      <!-- 背景和柔光云朵 -->
      <rect width="460" height="420" fill="url(#bgGrad)" />
      <path d="M295,12 C345,-5 415,28 430,80 C442,120 398,155 352,132 C315,114 265,68 295,12 Z" fill="#ffffff" fill-opacity="0.09" />
      <path d="M0,330 C52,295 110,332 162,365 C208,395 255,375 305,420 L0,420 Z" fill="#60a5fa" fill-opacity="0.16" />

      <!-- 轨道虚线环 -->
      <ellipse cx="235" cy="238" rx="170" ry="88" fill="none" stroke="#93c5fd" stroke-opacity="0.32" stroke-width="1.2" stroke-dasharray="4 5" />
      <ellipse cx="235" cy="238" rx="122" ry="62" fill="none" stroke="#bae6fd" stroke-opacity="0.35" stroke-width="1" />

      <!-- 顶部悬浮统计卡片 -->
      <g transform="translate(148, 72)">
        <rect width="62" height="36" rx="5" fill="#1e40af" fill-opacity="0.58" stroke="#60a5fa" stroke-opacity="0.55" />
        <line x1="8" y1="10" x2="34" y2="10" stroke="#93c5fd" stroke-width="2.5" stroke-linecap="round" />
        <line x1="8" y1="18" x2="50" y2="18" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" />
        <line x1="8" y1="26" x2="40" y2="26" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" />
        <circle cx="48" cy="10" r="4" fill="#38bdf8" />
      </g>

      <!-- 右上柱状图面板 -->
      <g transform="translate(308, 132) skewY(12)">
        <rect width="74" height="52" rx="6" fill="#0f3ea8" fill-opacity="0.72" stroke="#60a5fa" stroke-opacity="0.6" />
        <rect x="10" y="24" width="8" height="20" rx="2" fill="#38bdf8" />
        <rect x="24" y="16" width="8" height="28" rx="2" fill="#fb923c" />
        <rect x="38" y="20" width="8" height="24" rx="2" fill="#60a5fa" />
        <rect x="52" y="10" width="8" height="34" rx="2" fill="#fde047" />
      </g>

      <!-- 右下曲线面板 -->
      <g transform="translate(310, 212) skewY(-10)">
        <rect width="84" height="62" rx="6" fill="#1d4ed8" fill-opacity="0.68" stroke="#60a5fa" stroke-opacity="0.55" />
        <line x1="10" y1="16" x2="72" y2="16" stroke="#93c5fd" stroke-opacity="0.5" stroke-width="1.5" />
        <line x1="10" y1="28" x2="72" y2="28" stroke="#93c5fd" stroke-opacity="0.35" stroke-width="1.5" />
        <polyline points="10,48 26,38 42,44 58,28 74,34" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      </g>

      <!-- 弧形全息数据光幕 -->
      <path
        d="M84,186 C86,258 195,288 308,266 L308,314 C195,338 84,306 84,234 Z"
        fill="url(#screenGrad)"
        stroke="#bae6fd"
        stroke-opacity="0.65"
        stroke-width="1.5"
      />
      <!-- 弧形光幕内饼图与柱状图 -->
      <g transform="translate(105, 224)">
        <circle cx="14" cy="14" r="14" fill="#fbbf24" />
        <path d="M14,14 L14,0 A14,14 0 0,1 28,14 Z" fill="#f97316" />
        <path d="M14,14 L28,14 A14,14 0 0,1 14,28 Z" fill="#1d4ed8" />
      </g>
      <path d="M146,272 Q178,246 210,276 T282,262" fill="none" stroke="#e0f2fe" stroke-width="2" />
      <g fill="#bae6fd" fill-opacity="0.88">
        <rect x="234" y="274" width="6" height="24" rx="2" />
        <rect x="246" y="264" width="6" height="34" rx="2" />
        <rect x="258" y="270" width="6" height="28" rx="2" />
        <rect x="270" y="256" width="6" height="42" rx="2" />
        <rect x="282" y="266" width="6" height="32" rx="2" />
      </g>

      <!-- 笔记本发出光束 -->
      <polygon points="188,162 248,140 282,92 198,92" fill="url(#glowGrad)" />

      <!-- 坐在光幕上使用电脑的人物 -->
      <g transform="translate(182, 114)">
        <!-- 腿部 -->
        <path d="M62,74 L46,112 L58,116 L76,82 Z" fill="#1e3a8a" />
        <path d="M78,76 L72,118 L85,118 L92,80 Z" fill="#1d4ed8" />
        <!-- 鞋子 -->
        <ellipse cx="48" cy="116" rx="9" ry="4" fill="#0f172a" />
        <ellipse cx="78" cy="120" rx="9" ry="4" fill="#0f172a" />
        <!-- 西装上衣 -->
        <path d="M68,42 C82,42 96,52 94,76 L58,76 C56,56 60,42 68,42 Z" fill="#67e8f9" />
        <path d="M76,44 L84,74 L74,74 Z" fill="#2563eb" />
        <!-- 头部与头发 -->
        <circle cx="80" cy="24" r="13" fill="#fed7aa" />
        <path d="M68,22 C66,8 82,2 95,10 C102,15 98,26 91,26 C87,18 76,17 68,22 Z" fill="#1e293b" />
        <!-- 手臂 -->
        <path d="M70,54 L42,60 L44,68 L74,64 Z" fill="#38bdf8" />
        <!-- 笔记本电脑 -->
        <polygon points="10,44 46,56 40,72 6,58" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1" />
        <polygon points="46,56 66,64 60,72 40,72" fill="#cbd5e1" />
      </g>

      <!-- 左侧与底部小图标卡片 -->
      <g transform="translate(64, 294)">
        <circle cx="20" cy="20" r="18" fill="#1e40af" fill-opacity="0.7" stroke="#60a5fa" stroke-opacity="0.5" />
        <rect x="12" y="13" width="4" height="14" rx="1" fill="#e0f2fe" />
        <rect x="18" y="13" width="4" height="14" rx="1" fill="#e0f2fe" />
        <rect x="24" y="13" width="4" height="14" rx="1" fill="#e0f2fe" />
      </g>

      <g transform="translate(106, 336) rotate(-6)">
        <rect width="58" height="44" rx="6" fill="#eff6ff" fill-opacity="0.95" />
        <polygon points="6,36 22,18 36,30 44,22 52,36" fill="#38bdf8" />
        <circle cx="16" cy="14" r="4" fill="#fbbf24" />
      </g>

      <g transform="translate(216, 356)">
        <circle cx="20" cy="20" r="18" fill="#1e40af" fill-opacity="0.7" stroke="#60a5fa" stroke-opacity="0.55" />
        <rect x="11" y="14" width="18" height="12" rx="2" fill="#e0f2fe" />
        <line x1="11" y1="18" x2="29" y2="18" stroke="#1d4ed8" stroke-width="2" />
      </g>

      <g transform="translate(362, 336)">
        <circle cx="18" cy="18" r="16" fill="#1e40af" fill-opacity="0.65" stroke="#93c5fd" stroke-opacity="0.65" />
        <circle cx="18" cy="18" r="9" fill="none" stroke="#e0f2fe" stroke-width="1.3" />
        <ellipse cx="18" cy="18" rx="4.5" ry="9" fill="none" stroke="#e0f2fe" stroke-width="1.1" />
        <line x1="9" y1="18" x2="27" y2="18" stroke="#e0f2fe" stroke-width="1.1" />
      </g>

      <!-- 闪烁星点装饰 -->
      <path d="M74,116 L76,122 L82,124 L76,126 L74,132 L72,126 L66,124 L72,122 Z" fill="#ffffff" fill-opacity="0.9" />
      <path d="M402,118 L403.5,123 L408.5,124.5 L403.5,126 L402,131 L400.5,126 L395.5,124.5 L400.5,123 Z" fill="#e0f2fe" fill-opacity="0.85" />
      <polygon points="86,166 102,168 92,180" fill="#fbbf24" />
      <circle cx="350" cy="108" r="3" fill="#ffffff" fill-opacity="0.8" />
    </svg>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.login-illustration {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0b5ef2;
}

.illustration-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
