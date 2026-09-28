<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getEssayCorrect } from '@/api/essay.ts';
import NoDataView from '@/views/NoDataView.vue';

const route = useRoute();
const router = useRouter();

interface Correction {
  error: string;
  original: string;
  corrected: string;
  explanation: string;
  sentence: string; // 原文定位到的句子
  errorPart: string; // 句子中错误部分
  correctPart: string; // 修正后的结果
}

interface ScoreBreakdown {
  content: string;
  grammar: string;
  vocabulary: string;
  organization: string;
}

interface Score {
  total: string;
  breakdown: ScoreBreakdown;
}

interface Result {
  score: Score;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
  corrections: Correction[];
  suggestions: string[];
}

interface History {
  essayId: string;
  content: string;
  result: Result;
  createdAt: string;
}

interface PositionResult {
  text: string;
  start: number;
  end: number;
  found: boolean;
}

const isLoading = ref(true);
const activeCorrectionIndex = ref(0);
const isDataExist = ref(true);
const correctionsPanelExpanded = ref(false);
const touchStartX = ref<number>(0);
const touchEndX = ref<number>(0);
const panelOffset = ref<number>(0);
const showComparison = ref(false);


const record = ref<History>({
  essayId: '',
  content: '',
  result: {
    score: {
      total: '',
      breakdown: {
        content: '',
        grammar: '',
        vocabulary: '',
        organization: '',
      },
    },
    feedback: '',
    strengths: [],
    weaknesses: [],
    corrections: [],
    suggestions: [],
  },
  createdAt: ''
});

function position(content: string, sentence: string, errorPart: string): PositionResult {
  try {
    content = content.replace(/\n/g, ' ');
    sentence = sentence.replace(/\n/g, ' ');
    errorPart = errorPart.replace(/\n/g, ' ');

    const sentenceStart = content.indexOf(sentence);
    if (sentenceStart >= 0) {
      const errorStart = sentence.indexOf(errorPart);

      if (errorStart >= 0) {
        const fullStart = sentenceStart + errorStart;
        const fullEnd = fullStart + errorPart.length;

        return {
          text: content.substring(fullStart, fullEnd),
          start: fullStart,
          end: fullEnd,
          found: true
        };
      }
    }
  } catch (error) {
    console.error('Error during positioning:', error);
  }

  return {
    text: errorPart,
    start: -1,
    end: -1,
    found: false
  };
}

function highlightEssayContent(provider: 'h5' | 'web', isExport = false) {
  if (!record.value.content || record.value.result.corrections.length === 0) {
    return record.value.content;
  }

  const content = record.value.content;
  const corrections = record.value.result.corrections;

  let offset = 0;
  const highlightedParts = [];

  const correctionsWithPos = corrections.map((c, i) => ({
    ...c,
    originalIndex: i,
    pos: position(content, c.sentence, c.errorPart)
  })).filter(c => c.pos.found);

  const sortedCorrections = correctionsWithPos.sort((a, b) => a.pos.start - b.pos.start);

  sortedCorrections.forEach((correction) => {
    const index = correction.originalIndex;
    const pos = correction.pos;

    if (pos.start >= offset) {
      highlightedParts.push(content.substring(offset, pos.start));

      if (showComparison.value || isExport) {
        highlightedParts.push(
            `<span class="underline decoration-red-500 decoration-2 px-1 rounded">${ pos.text }</span>`
        );
      } else if (provider === 'h5') {
        highlightedParts.push(
            `<span class="md-correction-highlight underline decoration-red-500 decoration-2 cursor-pointer px-1 rounded"
                data-correction-index="${ index }"
                title="点击查看批改详情">${ pos.text }</span>`
        );
      } else {
        highlightedParts.push(
            `<span class="correction-highlight underline decoration-red-500 decoration-2 cursor-pointer px-1 rounded"
                data-correction-index="${ index }"
                title="点击查看批改详情">${ pos.text }</span>`
        );
      }

      offset = pos.end;
    }
  });

  if (offset < content.length) {
    highlightedParts.push(content.substring(offset));
  }

  return highlightedParts.join('');
}

function highlightCorrectedEssay(provider: 'h5' | 'web', isExport = false) {
  if (!record.value.content || record.value.result.corrections.length === 0) {
    return record.value.content;
  }

  const content = record.value.content;
  const corrections = record.value.result.corrections;

  let offset = 0;
  const highlightedParts = [];

  const correctionsWithPos = corrections.map((c, i) => ({
    ...c,
    originalIndex: i,
    pos: position(content, c.sentence, c.errorPart)
  })).filter(c => c.pos.found);

  const sortedCorrections = correctionsWithPos.sort((a, b) => a.pos.start - b.pos.start);

  sortedCorrections.forEach((correction) => {
    const index = correction.originalIndex;
    const pos = correction.pos;

    if (pos.start >= offset) {
      highlightedParts.push(content.substring(offset, pos.start));

      if (showComparison.value || isExport) {
        highlightedParts.push(
            `<span class="underline decoration-green-500 decoration-2 px-1 rounded bg-green-50">${ correction.correctPart }</span>`
        );
      } else if (provider === 'h5') {
        highlightedParts.push(
            `<span class="md-correction-highlight underline decoration-green-500 decoration-2 cursor-pointer px-1 rounded bg-green-50"
                data-correction-index="${ index }"
                title="修改后的内容">${ correction.correctPart }</span>`
        );
      } else {
        highlightedParts.push(
            `<span class="correction-highlight underline decoration-green-500 decoration-2 cursor-pointer px-1 rounded bg-green-50"
                data-correction-index="${ index }"
                title="修改后的内容">${ correction.correctPart }</span>`
        );
      }

      offset = pos.end;
    }
  });

  if (offset < content.length) {
    highlightedParts.push(content.substring(offset));
  }

  return highlightedParts.join('');
}

function getScoreLevel(score: number) {
  if (score >= 9) {
    return { level: '优秀', color: 'text-success' };
  }
  if (score >= 8) {
    return { level: '良好', color: 'text-primary' };
  }
  if (score >= 7) {
    return { level: '中等', color: 'text-accent-amber' };
  }
  if (score >= 6) {
    return { level: '及格', color: 'text-warning' };
  }
  return { level: '不及格', color: 'text-error' };
}

function getScoreColor(score: number) {
  if (score >= 9) {
    return 'var(--color-success)';
  }
  if (score >= 8) {
    return 'var(--color-primary)';
  }
  if (score >= 7) {
    return 'var(--color-accent-amber)';
  }
  if (score >= 6) {
    return 'var(--color-warning)';
  }
  return 'var(--color-error)';
}

function onCorrectionClick(index: number, provider: 'h5' | 'web') {
  activeCorrectionIndex.value = index;
  let className;
  if (provider === 'h5') {
    correctionsPanelExpanded.value = true;
    className = '.md-correction-highlight';
  } else {
    className = '.correction-highlight';
  }

  const elements = document.querySelectorAll(className);
  let currentEle;

  elements.forEach(element => {
    if (index === Number(element.getAttribute('data-correction-index'))) {
      currentEle = element;
    }
    element.classList.remove('focus');
  });

  currentEle!.classList.add('focus');

  if (provider === 'h5') {
    window?.scrollTo({
      top: currentEle!.offsetTop - 150,
      behavior: 'smooth'
    });
  }
}


function onToggleCorrectionsPanel() {
  correctionsPanelExpanded.value = !correctionsPanelExpanded.value;
  const elements = document.querySelectorAll('.md-correction-highlight');
  let currentEle;
  activeCorrectionIndex.value = 0;

  if (correctionsPanelExpanded.value) {
    elements.forEach(element => {
      if (activeCorrectionIndex.value === Number(element.getAttribute('data-correction-index'))) {
        currentEle = element;
      } else {
        element.classList.remove('focus');
      }
    });

    panelOffset.value = 70;
    currentEle!.classList.add('focus');

    setTimeout(() => {
      panelOffset.value = 0;
    }, 300);
  } else {
    elements.forEach(element => {
      element.classList.remove('focus');
    });
  }

  setTimeout(() => {
    panelOffset.value = 0;
  }, 300);
}

function previousCorrection() {
  if (activeCorrectionIndex.value > 0) {
    onCorrectionClick(activeCorrectionIndex.value - 1, 'h5');
  }
}

function nextCorrection() {
  if (activeCorrectionIndex.value < record.value.result.corrections.length - 1) {
    onCorrectionClick(activeCorrectionIndex.value + 1, 'h5');
  }
}

function handleSwipeStart(event: TouchEvent) {
  touchStartX.value = event.touches[0]!.clientX;
}

function handleSwipeEnd(event: TouchEvent) {
  touchEndX.value = event.changedTouches[0]!.clientX;
  handleSwipeGesture();
}


function handleSwipeGesture() {
  const swipeThreshold = 50; // 最小滑动距离阈值
  const deltaX = touchStartX.value - touchEndX.value;

  // 确保有修正项并且面板已展开
  if (!correctionsPanelExpanded.value || record.value.result.corrections.length <= 1) {
    return;
  }

  // 向左滑动 - 切换到下一个
  if (deltaX > swipeThreshold) {
    nextCorrection();
  }
  // 向右滑动 - 切换到上一个
  else if (deltaX < -swipeThreshold) {
    previousCorrection();
  }
}

function getCorrectionPositionInfo(correction: Correction) {
  return position(
      record.value.content,
      correction.sentence,
      correction.errorPart
  );
}

function exportResult() {
  const htmlContent = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>作文批改结果</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      background-color: #f8fafc;
      margin: 0;
      padding: 20px;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      padding: 30px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 1px solid #e2e8f0;
    }

    .title {
      font-size: 24px;
      font-weight: 600;
      color: #1e293b;
    }

    .timestamp {
      font-size: 14px;
      color: #64748b;
      display: flex;
      align-items: center;
    }

    .timestamp svg {
      margin-right: 8px;
    }

    .section {
      margin-bottom: 30px;
      padding: 20px;
      border-radius: 12px;
      background: linear-gradient(to right, #f8fafc, #f1f5f9);
      border: 1px solid #e2e8f0;
    }

    .section-title {
      font-size: 18px;
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 15px;
      display: flex;
      align-items: center;
    }

    .section-title svg {
      margin-right: 10px;
    }

    .essay-content {
      background: white;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      line-height: 1.8;
      white-space: pre-wrap;
      font-size: 16px;
    }

    .overall-score {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 20px;
    }

    .score-display {
      display: flex;
      align-items: center;
    }

    .score-number {
      font-size: 48px;
      font-weight: 700;
      color: #4f46e5;
      margin-right: 15px;
    }

    .score-max {
      font-size: 18px;
      color: #64748b;
    }

    .score-level {
      padding: 6px 12px;
      border-radius: 9999px;
      font-weight: 500;
      font-size: 16px;
      background-color: #e0e7ff;
      color: #4f46e5;
    }

    .breakdown-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 15px;
      margin-top: 20px;
    }

    .breakdown-item {
      background: white;
      border-radius: 8px;
      padding: 15px;
      text-align: center;
      border: 1px solid #e2e8f0;
    }

    .breakdown-label {
      font-size: 14px;
      color: #64748b;
      text-transform: capitalize;
      margin-bottom: 5px;
    }

    .breakdown-score {
      font-size: 20px;
      font-weight: 700;
    }

    .feedback-content {
      background: white;
      border-radius: 8px;
      padding: 20px;
      border: 1px solid #bae6fd;
      line-height: 1.8;
      font-size: 16px;
    }

    .list-section {
      background: white;
      border-radius: 8px;
      padding: 20px;
      border: 1px solid #e2e8f0;
    }

    .list-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 15px;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
    }

    .list-icon {
      flex-shrink: 0;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 12px;
      margin-top: 2px;
    }

    .corrections-container {
      background: white;
      border-radius: 8px;
      padding: 20px;
      border: 1px solid #e2e8f0;
    }

    .correction-card {
      border: 1px solid #c7d2fe;
      border-radius: 8px;
      margin-bottom: 20px;
      overflow: hidden;
    }

    .correction-header {
      padding: 15px 20px;
      border-bottom: 1px solid #e0e7ff;
      background-color: #eef2ff;
      font-weight: 600;
      color: #4f46e5;
    }

    .correction-body {
      padding: 20px;
    }

    .correction-field {
      margin-bottom: 15px;
    }

    .field-label {
      font-size: 14px;
      color: #64748b;
      margin-bottom: 5px;
    }

    .field-value {
      padding: 12px;
      border-radius: 6px;
      font-size: 16px;
      line-height: 1.6;
    }

    .original {
      background-color: #fef2f2;
      border: 1px solid #fecaca;
      color: #991b1b;
    }

    .corrected {
      background-color: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
    }

    .explanation {
      background-color: #eff6ff;
      border: 1px solid #bfdbfe;
      color: #1e40af;
    }

    .no-corrections {
      text-align: center;
      padding: 40px;
      color: #64748b;
      font-size: 16px;
    }

    .comparison-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .comparison-column {
      background: white;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid #cbd5e1;
    }

    .original-column {
      border-color: #fecaca;
    }

    .original-column .column-header {
      background-color: #fef2f2;
      color: #b91c1c;
      padding: 10px 15px;
      font-weight: 600;
      border-bottom: 1px solid #fecaca;
    }

    .corrected-column {
      border-color: #bbf7d0;
    }

    .corrected-column .column-header {
      background-color: #f0fdf4;
      color: #15803d;
      padding: 10px 15px;
      font-weight: 600;
      border-bottom: 1px solid #bbf7d0;
    }

    .comparison-column .essay-content {
      border: none;
      margin-bottom: 0;
      border-radius: 0;
    }

    .underline { text-decoration: underline; }
    .decoration-red-500 { text-decoration-color: #ef4444; }
    .decoration-green-500 { text-decoration-color: #22c55e; }
    .decoration-2 { text-decoration-thickness: 2px; text-underline-offset: 2px; }
    .px-1 { padding-left: 0.25rem; padding-right: 0.25rem; }
    .rounded { border-radius: 0.25rem; }
    .bg-green-50 { background-color: #f0fdf4; }

    @media (max-width: 768px) {
      .comparison-grid {
        grid-template-columns: 1fr;
      }
    }

    @media print {
      body {
        background-color: white;
        padding: 0;
      }

      .container {
        box-shadow: none;
        border-radius: 0;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="title">作文批改结果</h1>
      <div class="timestamp">
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        提交时间：${ record.value.createdAt }
      </div>
    </div>

    <!-- 作文内容 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        作文内容
      </h2>
      ${ record.value.result.corrections.length > 0 ? `
      <div class="comparison-grid">
        <div class="comparison-column original-column">
          <div class="column-header">原文</div>
          <div class="essay-content">${ highlightEssayContent('web', true).replace(/\n/g, '<br>') }</div>
        </div>
        <div class="comparison-column corrected-column">
          <div class="column-header">修改后</div>
          <div class="essay-content">${ highlightCorrectedEssay('web', true).replace(/\n/g, '<br>') }</div>
        </div>
      </div>
      ` : `
      <div class="essay-content">${ record.value.content.replace(/\n/g, '<br>') }</div>
      ` }
    </div>

    <!-- 总体评分 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        总体评分
      </h2>
      <div class="overall-score">
        <div class="score-display">
          <div class="score-number">${ record.value.result.score.total }</div>
          <div>
            <div class="score-max">/10</div>
          </div>
        </div>
        <div class="score-level">${ getScoreLevel(parseFloat(record.value.result.score.total)).level }</div>
      </div>

      <!-- 分项评分 -->
      <div class="breakdown-grid">
        ${ Object.entries(record.value.result.score.breakdown).map(([category, score]) => `
        <div class="breakdown-item">
          <div class="breakdown-label">${ category }</div>
          <div class="breakdown-score" style="color: ${ getScoreColor(parseFloat(score)) };">${ score }</div>
        </div>
        `).join('') }
      </div>
    </div>

    <!-- AI评语 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        AI评语
      </h2>
      <div class="feedback-content">${ record.value.result.feedback }</div>
    </div>

    <!-- 优点亮点 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        优点亮点
      </h2>
      <div class="list-section">
        ${ record.value.result.strengths.map(strength => `
        <div class="list-item">
          <div class="list-icon" style="background-color: #dcfce7;">
            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #22c55e;">
              <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            </svg>
          </div>
          <div>${ strength }</div>
        </div>
        `).join('') }
      </div>
    </div>

    <!-- 待改进之处 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        待改进之处
      </h2>
      <div class="list-section">
        ${ record.value.result.weaknesses.map(weakness => `
        <div class="list-item">
          <div class="list-icon" style="background-color: #fef3c7;">
            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #f59e0b;">
              <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            </svg>
          </div>
          <div>${ weakness }</div>
        </div>
        `).join('') }
      </div>
    </div>

    <!-- 学习建议 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        学习建议
      </h2>
      <div class="list-section">
        ${ record.value.result.suggestions.map(suggestion => `
        <div class="list-item">
          <div class="list-icon" style="background-color: #cffafe;">
            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #06b6d4;">
              <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            </svg>
          </div>
          <div>${ suggestion }</div>
        </div>
        `).join('') }
      </div>
    </div>

    <!-- 修改建议 -->
    <div class="section">
      <h2 class="section-title">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        修改建议
      </h2>
      <div class="corrections-container">
        ${ record.value.result.corrections.length > 0 ?
      record.value.result.corrections.map((correction, index) => `
        <div class="correction-card">
          <div class="correction-header">
            <div style="display: flex; align-items: center;">
              <div style="width: 24px; height: 24px; border-radius: 50%; background-color: #4f46e5; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                <span style="color: white; font-weight: bold; font-size: 12px;">${ index + 1 }</span>
              </div>
              ${ correction.error }
            </div>
          </div>
          <div class="correction-body">
            <div class="correction-field">
              <div class="field-label">原句：</div>
              <div class="field-value original">${ correction.original }</div>
            </div>
            <div class="correction-field">
              <div class="field-label">修改后：</div>
              <div class="field-value corrected">${ correction.corrected }</div>
            </div>
            <div class="correction-field">
              <div class="field-label">说明：</div>
              <div class="field-value explanation">${ correction.explanation }</div>
            </div>
          </div>
        </div>
        `).join('') :
      '<div class="no-corrections">恭喜！没有发现需要修改的地方。</div>' }
      </div>
    </div>
  </div>
</body>
</html>
  `;

  const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `作文批改结果_${ new Date().toISOString().slice(0, 10) }.html`;

  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function onLeftClick() {
  router.back();
}

function calculateWords(content: string) {
  const trimmed = content.trim();
  if (!trimmed) {
    return 0;
  }

  const isAsciiOnly = /^[\x20-\x7E]*$/.test(trimmed);
  if (isAsciiOnly) {
    return trimmed.split(/\s+/).filter(word => word.length > 0).length;
  } else {
    return trimmed.replace(/\s+/g, '').length;
  }
}

function previousWebCorrection() {
  if (activeCorrectionIndex.value > 0) {
    onCorrectionClick(activeCorrectionIndex.value - 1, 'web');
  }
}

function nextWebCorrection() {
  if (activeCorrectionIndex.value < record.value.result.corrections.length - 1) {
    onCorrectionClick(activeCorrectionIndex.value + 1, 'web');
  }
}

function goToWebCard(index: number) {
  onCorrectionClick(index, 'web');
}


function bindCorrectionClickEvents() {
  document.querySelectorAll('.correction-highlight').forEach(element => {
    element.addEventListener('click', (event) => {
      if (showComparison.value) return;
      const index = parseInt((event.target as HTMLElement).getAttribute('data-correction-index') ?? '0');
      onCorrectionClick(index, 'web');
    });
  });

  document.querySelectorAll('.md-correction-highlight').forEach(element => {
    element.addEventListener('click', (event) => {
      if (showComparison.value) return;
      const index = parseInt((event.target as HTMLElement).getAttribute('data-correction-index') ?? '0');
      onCorrectionClick(index, 'h5');
    });
  });
}

watch(showComparison, (newValue: boolean) => {
  if (newValue) {
    activeCorrectionIndex.value = 0;
    correctionsPanelExpanded.value = false;
  } else {
    setTimeout(() => {
      bindCorrectionClickEvents();
    }, 100);
  }
});

onMounted(async () => {
  try {
    isLoading.value = true;
    const res = await getEssayCorrect(route.params.id as string);
    record.value = res.data;

    if (record.value.result.corrections.length > 0) {
      activeCorrectionIndex.value = 0;
    }

    setTimeout(() => {
      bindCorrectionClickEvents();
    }, 100);
  } catch (_) {
    isDataExist.value = false;
  } finally {
    isLoading.value = false;
  }

});
</script>

<template>
  <template v-if="!isDataExist">
    <no-data-view/>
  </template>
  <template v-else>
    <div>
      <!-- web -->
      <div class="min-h-screen py-24 px-3 hidden md:block bg-canvas">
        <transition name="fade-from-bottom">
          <template v-if="!isLoading">
            <div class="max-w-7xl mx-auto">
              <div class="bg-surface-card rounded-[8px] p-6 border border-hairline">
                <div class="flex justify-between items-center mb-6">
                  <h2 class="text-[28px] font-display font-normal text-ink">批改结果</h2>
                  <button
                      class="cursor-pointer flex items-center text-[14px] px-4 py-2 rounded-[8px] border transition-all duration-200 bg-canvas text-primary border-primary/30 hover`:bg-primary hover:text-on-primary hover:border-primary"
                      @click="exportResult"
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                          stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                    </svg>
                    导出结果
                  </button>
                </div>

                <!-- 主要内容区域 - 左右两栏布局 -->
                <div class="flex flex-col lg:flex-row gap-6">
                  <!-- 左侧栏：作文内容和其他信息 -->
                  <div :class="showComparison ? 'lg:w-full' : 'lg:w-7/12'">
                    <!-- 作文内容和时间 -->
                    <div
                        :class="['bg-surface-soft rounded-[8px] p-5 border border-hairline mb-6 en-font', showComparison ? 'comparison-mode' : '']">
                      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 gap-3">
                        <h3 class="font-medium text-ink flex items-center text-lg">
                          <svg class="w-5 h-5 mr-2 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          {{ showComparison ? '作文对比' : '作文内容' }}
                        </h3>
                        <template v-if="record.result.corrections.length > 0">
                          <button
                              :class="['cursor-pointer flex items-center text-[14px] px-4 py-2 rounded-[6px] border transition-all duration-200',
                              showComparison
                                ? 'bg-primary text-on-primary border-primary'
                                : 'bg-canvas text-primary border-primary/30 hover:bg-primary/5']"
                              @click="showComparison = !showComparison"
                          >
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                                    stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                            </svg>
                            {{ showComparison ? '关闭对比' : '查看对比' }}
                          </button>
                        </template>
                      </div>

                      <template v-if="!showComparison">
                        <div
                            class="bg-canvas rounded-[6px] p-4 border border-hairline mb-3 text-ink leading-relaxed text-base whitespace-pre-wrap"
                            v-html="highlightEssayContent('web')">
                        </div>
                      </template>

                      <template v-else>
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-3">
                          <div class="bg-canvas rounded-[6px] p-4 border border-error/20">
                            <div class="flex items-center mb-3 pb-2 border-b border-error/10">
                              <svg class="w-5 h-5 mr-2 text-error" fill="none" stroke="currentColor"
                                   viewBox="0 0 24 24">
                                <path
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                    stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                              </svg>
                              <span class="font-semibold text-error">原文</span>
                            </div>
                            <div
                                class="text-ink leading-relaxed text-base whitespace-pre-wrap"
                                v-html="highlightEssayContent('web')">
                            </div>
                          </div>

                          <div class="bg-canvas rounded-[6px] p-4 border border-success/20">
                            <div class="flex items-center mb-3 pb-2 border-b border-success/10">
                              <svg class="w-5 h-5 mr-2 text-success" fill="none" stroke="currentColor"
                                   viewBox="0 0 24 24">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                      stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                              </svg>
                              <span class="font-semibold text-success">修改后</span>
                            </div>
                            <div
                                class="text-ink leading-relaxed text-base whitespace-pre-wrap"
                                v-html="highlightCorrectedEssay('web')">
                            </div>
                          </div>
                        </div>
                      </template>

                      <div class="text-base text-muted flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        {{ record.createdAt }}
                      </div>
                      <div class="text-base text-muted flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        <span>{{ calculateWords(record.content) }}字</span>
                      </div>
                    </div>

                    <!-- 总体评分和其他内容 - 仅在非对比模式显示 -->
                    <template v-if="!showComparison">
                      <div class="bg-surface-soft rounded-[8px] p-5 border border-hairline">
                        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div>
                            <h3 class="font-medium text-ink text-lg">总体评分</h3>
                            <p class="text-[14px] text-muted mt-1">基于多个维度综合评估</p>
                          </div>
                          <div class="flex items-center">
                            <div class="text-4xl font-display font-normal text-primary mr-4">
                              {{ record.result.score.total }}
                              <span class="text-lg text-muted">/10</span>
                            </div>
                            <div class="px-3 py-1 rounded-full bg-primary/10 text-primary font-medium text-[14px]">
                              {{ getScoreLevel(parseFloat(record.result.score.total)).level }}
                            </div>
                          </div>
                        </div>

                        <!-- 分项评分 -->
                        <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                          <template v-for="(score, category) in record.result.score.breakdown" :key="category">
                            <div
                                class="bg-canvas rounded-[6px] p-3 border border-hairline text-center">
                              <div class="text-[14px] text-muted capitalize">{{ category }}</div>
                              <div :class="getScoreLevel(parseFloat(score)).color"
                                   class="text-xl font-medium mt-1">{{ score }}
                              </div>
                            </div>
                          </template>
                        </div>
                      </div>

                      <!-- AI评语 -->
                      <div class="mt-6 bg-surface-soft rounded-[8px] p-5 border border-hairline">
                        <h3 class="font-medium text-ink flex items-center text-lg">
                          <svg class="w-5 h-5 mr-2 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          AI评语
                        </h3>
                        <p class="mt-3 text-ink leading-relaxed text-[14px]">{{ record.result.feedback }}</p>
                      </div>

                      <!-- 优点亮点 -->
                      <div
                          class="mt-6 bg-surface-soft rounded-[8px] p-5 border border-hairline">
                        <h3 class="font-medium text-ink flex items-center text-lg">
                          <svg class="w-5 h-5 mr-2 text-success" fill="none" stroke="currentColor"
                               viewBox="0 0 24 24">
                            <path
                                d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          优点亮点
                        </h3>
                        <ul class="mt-3 space-y-2">
                          <template v-for="strength in record.result.strengths">
                            <li class="flex items-start p-3 bg-canvas rounded-[6px] border border-hairline">
                              <div class="flex-shrink-0 mt-1 mr-3">
                                <div class="w-5 h-5 rounded-full bg-success flex items-center justify-center">
                                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"
                                          stroke-width="2"/>
                                  </svg>
                                </div>
                              </div>
                              <span class="text-ink text-[14px]">{{ strength }}</span>
                            </li>
                          </template>
                        </ul>
                      </div>

                      <!-- 待改进之处 -->
                      <div
                          class="mt-6 bg-surface-soft rounded-[8px] p-5 border border-hairline">
                        <h3 class="font-medium text-ink flex items-center text-lg">
                          <svg class="w-5 h-5 mr-2 text-warning" fill="none" stroke="currentColor"
                               viewBox="0 0 24 24">
                            <path
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          待改进之处
                        </h3>
                        <ul class="mt-3 space-y-2">
                          <template v-for="weakness in record.result.weaknesses">
                            <li class="flex items-start p-3 bg-canvas rounded-[6px] border border-hairline">
                              <div class="flex-shrink-0 mt-1 mr-3">
                                <div class="w-5 h-5 rounded-full bg-warning flex items-center justify-center">
                                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"
                                          stroke-width="2"/>
                                  </svg>
                                </div>
                              </div>
                              <span class="text-ink text-[14px]">{{ weakness }}</span>
                            </li>
                          </template>
                        </ul>
                      </div>

                      <!-- 学习建议 -->
                      <div class="mt-6 bg-surface-soft rounded-[8px] p-5 border border-hairline">
                        <h3 class="font-medium text-ink flex items-center text-lg">
                          <svg class="w-5 h-5 mr-2 text-accent-teal" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          学习建议
                        </h3>
                        <ul class="space-y-2 mt-3">
                          <template v-for="suggestion in record.result.suggestions">
                            <li class="flex items-start p-3 bg-canvas rounded-[6px] border border-hairline">
                              <div class="flex-shrink-0 mt-1 mr-3">
                                <div class="w-5 h-5 rounded-full bg-accent-teal flex items-center justify-center">
                                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"
                                          stroke-width="2"/>
                                  </svg>
                                </div>
                              </div>
                              <span class="text-ink text-[14px]">{{ suggestion }}</span>
                            </li>
                          </template>
                        </ul>
                      </div>
                    </template>
                  </div>

                  <!-- 右侧栏：修改建议 -->
                  <template v-if="!showComparison">
                    <div class="lg:w-5/12">
                      <div class="sticky top-8">
                        <div
                            class="bg-surface-soft rounded-[8px] p-5 border border-hairline">
                          <h3 class="font-medium text-ink flex items-center text-lg">
                            <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor"
                                 viewBox="0 0 24 24">
                              <path
                                  d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                                  stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                            </svg>
                            修改建议
                          </h3>

                          <template v-if="record.result.corrections.length > 0">
                            <div class="mt-4">
                              <div class="flex items-center justify-between mb-3">
                                <button
                                    :class="['flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200',
                                    activeCorrectionIndex === 0 ? 'bg-surface-soft text-muted-soft cursor-not-allowed' : 'bg-canvas text-primary hover:bg-primary/5 border border-primary/30 cursor-pointer']"
                                    :disabled="activeCorrectionIndex === 0"
                                    @click="previousWebCorrection"
                                >
                                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M15 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round"
                                          stroke-width="2"/>
                                  </svg>
                                </button>
                                <span class="text-caption text-muted font-medium">
                                {{ activeCorrectionIndex + 1 }} / {{ record.result.corrections.length }}
                              </span>
                                <button
                                    :class="['flex items-center justify-center w-10 h-10 rounded-full transition-all duration-200',
                                    (activeCorrectionIndex === record.result.corrections.length - 1) ? 'bg-surface-soft text-muted-soft cursor-not-allowed' : 'bg-canvas text-primary hover:bg-primary/5 border border-primary/30 cursor-pointer']"
                                    :disabled="activeCorrectionIndex === record.result.corrections.length - 1"
                                    @click="nextWebCorrection"
                                >
                                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round"
                                          stroke-width="2"/>
                                  </svg>
                                </button>
                              </div>

                              <div class="overflow-hidden">
                                <div :style="{ transform: `translateX(-${activeCorrectionIndex * 100}%)` }"
                                     class="transition-transform duration-300 ease-out">
                                  <div class="flex">
                                    <template v-for="(correction, index) in record.result.corrections" :key="index">
                                      <div class="w-full flex-shrink-0 px-1">
                                        <div :class="['bg-canvas rounded-[6px] border overflow-hidden transition-all duration-300',
                                           activeCorrectionIndex === index ? 'border-primary shadow-sm' : 'border-hairline']"
                                             class="correction-card"
                                             @click="onCorrectionClick(index, 'web')">
                                          <div
                                              :class="activeCorrectionIndex === index ? 'bg-primary/10 border-hairline' : 'bg-surface-soft border-hairline'"
                                              class="p-4 border-b">
                                            <div class="flex items-center">
                                              <div
                                                  class="w-6 h-6 rounded-full bg-primary flex items-center justify-center mr-2">
                                                <span class="text-white text-xs font-bold">{{ index + 1 }}</span>
                                              </div>
                                              <span class="font-medium text-primary text-[14px]">{{
                                                  correction.error
                                                }}</span>
                                              <template v-if="getCorrectionPositionInfo(correction).found">
                                          <span
                                              class="ml-2 text-caption text-muted-soft">
                                            (位置: {{ getCorrectionPositionInfo(correction).start }}-{{
                                              getCorrectionPositionInfo(correction).end
                                            }})
                                          </span>
                                              </template>
                                            </div>
                                          </div>

                                          <div class="p-4">
                                            <div class="mb-3">
                                              <div class="text-caption text-muted mb-1">原句：</div>
                                              <div
                                                  class="bg-error/5 p-3 rounded-[4px] border border-error/20 text-ink text-[14px] font-medium leading-relaxed">
                                                {{ correction.original }}
                                              </div>
                                            </div>

                                            <div class="mb-3">
                                              <div class="text-caption text-muted mb-1">修改后：</div>
                                              <div
                                                  class="bg-success/5 p-3 rounded-[4px] border border-success/20 text-ink text-[14px] font-medium leading-relaxed">
                                                {{ correction.corrected }}
                                              </div>
                                            </div>
                                            <div>
                                              <div class="text-caption text-muted mb-1">说明：</div>
                                              <div
                                                  class="bg-surface-soft p-3 rounded-[4px] border border-hairline text-[14px] text-ink leading-relaxed">
                                                {{ correction.explanation }}
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    </template>
                                  </div>
                                </div>
                              </div>

                              <div class="flex justify-center gap-2 mt-4">
                                <template v-for="(_, index) in record.result.corrections" :key="index">
                                  <button
                                      :class="['w-2 h-2 rounded-full transition-all duration-200 cursor-pointer',
                                      activeCorrectionIndex === index ? 'bg-primary w-6' : 'bg-hairline hover:bg-muted-soft']"
                                      @click="goToWebCard(index)"
                                  ></button>
                                </template>
                              </div>
                            </div>
                          </template>
                          <template v-else>
                            <div class="text-center py-8 text-muted text-[14px]">
                              恭喜！没有发现需要修改的地方。
                            </div>
                          </template>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </template>
        </transition>
      </div>

      <!--  h5 -->
      <div class="md:hidden min-h-screen flex flex-col">
        <transition-group name="fade-from-bottom">
          <template v-if="!isLoading">
            <div class="h-12">
              <t-navbar left-arrow title="作文批改" @left-click="onLeftClick"/>
            </div>

            <div class="pt-10 pb-36 px-3 space-y-4">
              <!-- 作文内容卡片 -->
              <div
                  :class="['bg-white rounded-xl border border-gray-200 overflow-hidden', showComparison ? 'comparison-mode' : '']">
                <div class="p-4 border-b border-gray-100">
                  <div class="flex flex-col gap-3">
                    <div class="flex justify-between items-center">
                      <div class="font-medium text-gray-800 text-base flex items-center">
                        <svg class="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        {{ showComparison ? '作文对比' : '作文内容' }}
                      </div>
                      <template v-if="record.result.corrections.length > 0">
                        <button
                            :class="['cursor-pointer flex items-center text-xs px-3 py-1.5 rounded-lg border transition-all duration-200',
                            showComparison
                              ? 'bg-indigo-600 text-white border-indigo-600'
                              : 'bg-white text-indigo-600 border-indigo-200 hover:bg-indigo-50']"
                            @click="showComparison = !showComparison"
                        >
                          <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                                  stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          {{ showComparison ? '关闭' : '对比' }}
                        </button>
                      </template>
                    </div>
                    <div class="flex justify-between items-center text-sm text-gray-500">
                      <div class="flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"/>
                        </svg>
                        {{ record.createdAt }}
                      </div>
                      <div class="flex items-center gap-2">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                              stroke-linecap="round" stroke-linejoin="round"
                              stroke-width="2"/>
                        </svg>
                        <span>{{ calculateWords(record.content) }}字</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="p-4">
                  <template v-if="!showComparison">
                    <div
                        class="text-gray-800 leading-relaxed text-sm whitespace-pre-wrap mb-3"
                        v-html="highlightEssayContent('h5')"
                    ></div>
                  </template>

                  <template v-else>
                    <div class="space-y-4">
                      <div class="bg-white rounded-lg p-3 border border-red-200">
                        <div class="flex items-center mb-2 pb-1 border-b border-red-100">
                          <svg class="w-4 h-4 mr-1.5 text-red-500" fill="none" stroke="currentColor"
                               viewBox="0 0 24 24">
                            <path
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          <span class="font-semibold text-red-700 text-xs">原文</span>
                        </div>
                        <div
                            class="text-gray-800 leading-relaxed text-sm whitespace-pre-wrap"
                            v-html="highlightEssayContent('h5')"
                        ></div>
                      </div>

                      <div class="bg-white rounded-lg p-3 border border-green-200">
                        <div class="flex items-center mb-2 pb-1 border-b border-green-100">
                          <svg class="w-4 h-4 mr-1.5 text-green-500" fill="none" stroke="currentColor"
                               viewBox="0 0 24 24">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                  stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                          </svg>
                          <span class="font-semibold text-green-700 text-xs">修改后</span>
                        </div>
                        <div
                            class="text-gray-800 leading-relaxed text-sm whitespace-pre-wrap"
                            v-html="highlightCorrectedEssay('h5')"
                        ></div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>

              <!-- 总体评分和其他内容 - 仅在非对比模式显示 -->
              <template v-if="!showComparison">
                <!-- 总体评分卡片 -->
                <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <div class="p-4 border-b border-gray-100">
                    <h3 class="font-medium text-gray-800 text-base flex items-center">
                      <svg class="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                      </svg>
                      总体评分
                    </h3>
                  </div>
                  <div class="p-4">
                    <!-- 总分展示 -->
                    <div class="flex items-center justify-between mb-4">
                      <div class="flex items-center">
                        <div class="text-3xl font-bold text-indigo-600 mr-3">
                          {{ record.result.score.total }}
                          <span class="text-base text-gray-500">/10</span>
                        </div>
                        <div class="px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 font-medium text-sm">
                          {{ getScoreLevel(parseFloat(record.result.score.total)).level }}
                        </div>
                      </div>
                    </div>

                    <!-- 分项评分 -->
                    <div class="grid grid-cols-2 gap-3">
                      <template v-for="(score, category) in record.result.score.breakdown" :key="category">
                        <div class="bg-gray-50 rounded-lg p-3 text-center">
                          <div class="text-sm text-gray-600 capitalize">{{ category }}</div>
                          <div :class="getScoreLevel(parseFloat(score)).color"
                               class="text-lg font-bold mt-1">{{ score }}
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>

                <!-- AI评语卡片 -->
                <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <div class="p-4 border-b border-gray-100">
                    <h3 class="font-medium text-gray-800 text-base flex items-center">
                      <svg class="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                      </svg>
                      AI评语
                    </h3>
                  </div>
                  <div class="p-4">
                    <p class="text-gray-800 leading-relaxed text-sm">{{ record.result.feedback }}</p>
                  </div>
                </div>

                <!-- 优点亮点卡片 -->
                <template v-if="record.result.strengths.length > 0">
                  <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                    <div class="p-4 border-b border-gray-100">
                      <h3 class="font-medium text-gray-800 text-base flex items-center">
                        <svg class="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        优点亮点
                      </h3>
                    </div>
                    <div class="p-4">
                      <div class="space-y-3">
                        <template v-for="strength in record.result.strengths">
                          <div class="flex items-start p-3 bg-green-50 rounded-lg border border-green-200">
                            <div class="flex-shrink-0 mt-0.5 mr-3">
                              <div class="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center">
                                <svg class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor"
                                     viewBox="0 0 24 24">
                                  <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"
                                        stroke-width="2"/>
                                </svg>
                              </div>
                            </div>
                            <span class="text-gray-800 text-sm">{{ strength }}</span>
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 待改进之处卡片 -->
                <template v-if="record.result.weaknesses.length > 0">
                  <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                    <div class="p-4 border-b border-gray-100">
                      <h3 class="font-medium text-gray-800 text-base flex items-center">
                        <svg class="w-5 h-5 mr-2 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        待改进之处
                      </h3>
                    </div>
                    <div class="p-4">
                      <div class="space-y-3">
                        <template v-for="weakness in record.result.weaknesses">
                          <div class="flex items-start p-3 bg-amber-50 rounded-lg border border-amber-200">
                            <div class="flex-shrink-0 mt-0.5 mr-3">
                              <div class="w-4 h-4 rounded-full bg-amber-500 flex items-center justify-center">
                                <svg class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor"
                                     viewBox="0 0 24 24">
                                  <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"
                                        stroke-width="2"/>
                                </svg>
                              </div>
                            </div>
                            <span class="text-gray-800 text-sm">{{ weakness }}</span>
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 学习建议卡片 -->
                <template v-if="record.result.suggestions.length > 0">
                  <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
                    <div class="p-4 border-b border-gray-100">
                      <h3 class="font-medium text-gray-800 text-base flex items-center">
                        <svg class="w-5 h-5 mr-2 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                              stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                        </svg>
                        学习建议
                      </h3>
                    </div>
                    <div class="p-4">
                      <div class="space-y-3">
                        <template v-for="suggestion in record.result.suggestions">
                          <div class="flex items-start p-3 bg-cyan-50 rounded-lg border border-cyan-200">
                            <div class="flex-shrink-0 mt-0.5 mr-3">
                              <div class="w-4 h-4 rounded-full bg-cyan-500 flex items-center justify-center">
                                <svg class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor"
                                     viewBox="0 0 24 24">
                                  <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"
                                        stroke-width="2"/>
                                </svg>
                              </div>
                            </div>
                            <span class="text-gray-800 text-sm">{{ suggestion }}</span>
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                </template>
              </template>

              <!-- 底部修改建议固定区域 -->
              <template v-if="record.result.corrections.length > 0 && !showComparison">
                <div
                    :style="{ transform: `translateY(${panelOffset}px)`}"
                    class="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl bg-white border-t  border-gray-200 shadow-lg transition-transform duration-300 ease-out"
                >
                  <!-- 展开/收起控制栏 -->
                  <div
                      class="flex items-center justify-between p-4 rounded-t-2xl bg-gradient-to-r from-violet-50 to-purple-50 border-b border-violet-100 cursor-pointer select-none"
                      @click="onToggleCorrectionsPanel"
                  >
                    <div class="flex items-center">
                      <svg class="w-5 h-5 mr-2 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                            stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                      </svg>
                      <h3 class="font-medium text-gray-800 text-base">修改建议</h3>
                      <span class="ml-2 px-2 py-0.5 bg-violet-100 text-violet-700 text-xs rounded-full">
                      {{ record.result.corrections.length }}
                    </span>
                    </div>
                    <div class="flex items-center">
                    <span class="text-xs text-gray-500 mr-2">
                      {{ correctionsPanelExpanded ? '收起' : '展开' }}
                    </span>
                      <svg
                          :class="correctionsPanelExpanded ? 'transform rotate-180' : ''"
                          class="w-4 h-4 text-gray-500 transition-transform duration-200"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                      >
                        <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                      </svg>
                    </div>
                  </div>

                  <!-- 修改建议内容区域 -->
                  <div
                      :class="correctionsPanelExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'"
                      class="transition-all duration-500 ease-out"
                      @touchend="handleSwipeEnd"
                      @touchstart="handleSwipeStart"
                  >
                    <div class="p-4 h-96 overflow-auto">
                      <template
                          v-if="record.result.corrections[activeCorrectionIndex]">
                        <div>
                          <div class="border border-violet-500 rounded-lg overflow-hidden shadow-lg bg-violet-50">
                            <div class="bg-violet-100 border-violet-200 p-3 border-b">
                              <div class="flex items-center">
                                <div class="w-6 h-6 rounded-full bg-violet-500 flex items-center justify-center mr-3">
                                  <span class="text-white text-sm font-bold">{{ activeCorrectionIndex + 1 }}</span>
                                </div>
                                <span class="font-medium text-violet-700 text-base">{{
                                    record.result.corrections[activeCorrectionIndex]?.error
                                  }}</span>
                              </div>
                            </div>

                            <div class="p-4 space-y-3">
                              <div class="grid grid-cols-1 gap-3">
                                <div>
                                  <div class="text-xs text-gray-500 mb-2 font-medium flex items-center">
                                    <svg class="w-3 h-3 mr-1 text-red-500" fill="none" stroke="currentColor"
                                         viewBox="0 0 24 24">
                                      <path
                                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"
                                          stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                                    </svg>
                                    原句：
                                  </div>
                                  <div
                                      class="bg-red-50 p-3 rounded-lg border border-red-200 text-gray-800 text-sm leading-relaxed">
                                    {{ record.result.corrections[activeCorrectionIndex]?.original }}
                                  </div>
                                </div>

                                <div>
                                  <div class="text-xs text-gray-500 mb-2 font-medium flex items-center">
                                    <svg class="w-3 h-3 mr-1 text-green-500" fill="none" stroke="currentColor"
                                         viewBox="0 0 24 24">
                                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"
                                            stroke-linejoin="round" stroke-width="2"/>
                                    </svg>
                                    修改后：
                                  </div>
                                  <div
                                      class="bg-green-50 p-3 rounded-lg border border-green-200 text-gray-800 text-sm leading-relaxed">
                                    {{ record.result.corrections[activeCorrectionIndex]?.corrected }}
                                  </div>
                                </div>
                              </div>

                              <div>
                                <div class="text-xs text-gray-500 mb-2 font-medium flex items-center">
                                  <svg class="w-3 h-3 mr-1 text-blue-500" fill="none" stroke="currentColor"
                                       viewBox="0 0 24 24">
                                    <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                          stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                                  </svg>
                                  说明：
                                </div>
                                <div
                                    class="bg-blue-50 p-3 rounded-lg border border-blue-200 text-gray-800 text-sm leading-relaxed">
                                  {{ record.result.corrections[activeCorrectionIndex]?.explanation }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </template>
        </transition-group>
      </div>
    </div>
  </template>
</template>

<style scoped>
:deep(.correction-highlight) {
  box-shadow: 0 0 0 rgba(0, 0, 0, 0);
  transition: all 0.3s ease;
  text-underline-offset: 5px;
}

:deep(.comparison-mode) {
  text-underline-offset: 5px;
}

:not(.comparison-mode) :deep(.correction-highlight:hover) {
  background-color: rgba(165, 21, 21, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

:deep(.md-correction-highlight) {
  box-shadow: 0 0 0 rgba(0, 0, 0, 0);
  transition: all 0.3s ease;
  text-underline-offset: 5px;
}

:not(.comparison-mode) :deep(.md-correction-highlight:hover) {
  background-color: rgba(165, 21, 21, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

:not(.comparison-mode) :deep(.focus) {
  background-color: rgba(165, 21, 21, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>