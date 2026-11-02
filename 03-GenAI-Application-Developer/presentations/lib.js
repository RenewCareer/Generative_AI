// Infographic templates for the course decks. Every visual is a native, editable PowerPoint
// shape or chart, and every colour comes from the theme, so one edit restyles all the decks.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./apply_theme.js");

const THEME = {
  name: "GenAI Course",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "14262B", lt1: "FFFFFF", dk2: "0B3B40", lt2: "E8F3F2",
    accent1: "0F766E", accent2: "C2452D", accent3: "F2A93B",
    accent4: "3B5BA5", accent5: "5EEAD4", accent6: "5B6F75",
    hlink: "0F766E", folHlink: "3B5BA5",
  },
};

const W = 13.33;
const H = 7.5;
const M = 0.6;
const CW = W - 2 * M;
const TOP = 1.5;
const BOTTOM = 6.85;
const CODE_FONT = "Courier New";
const warnings = [];

function buildDeck(deck) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.title = deck.title;
  pres.author = "GenAI Application Developer Track";
  pres.company = "GenAI Application Developer Track";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  const COLORS = {
    teal: { fill: C.accent1, ink: C.background1 },
    coral: { fill: C.accent2, ink: C.background1 },
    amber: { fill: C.accent3, ink: C.text1 },
    indigo: { fill: C.accent4, ink: C.background1 },
    mint: { fill: C.accent5, ink: C.text1 },
    slate: { fill: C.accent6, ink: C.background1 },
    deep: { fill: C.text2, ink: C.background1 },
  };
  const palette = ["teal", "indigo", "coral", "amber", "slate", "deep"];
  const colorOf = (item, index) => COLORS[item.color || palette[index % palette.length]];

  const footer = [
    {
      text: {
        text: `GenAI Application Developer  |  ${deck.module}`,
        options: { x: M, y: 7.0, w: 9, h: 0.3, fontSize: 11, color: C.accent6, margin: 0 },
      },
    },
  ];
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    objects: [
      {
        placeholder: {
          options: { name: "title", type: "title", x: M, y: 0.38, w: CW, h: 1.0, fontSize: 28, bold: true, color: C.text2, align: "left", valign: "top", margin: 0 },
          text: "",
        },
      },
      ...footer,
    ],
    slideNumber: { x: 12.2, y: 7.0, w: 0.55, h: 0.3, fontSize: 11, color: C.accent6, align: "right" },
  });
  pres.defineSlideMaster({
    title: "DARK",
    background: { color: C.text2 },
    objects: [
      {
        placeholder: {
          options: { name: "title", type: "title", x: M, y: 0.6, w: CW, h: 1.35, fontSize: 40, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 },
          text: "",
        },
      },
    ],
    slideNumber: { x: 12.2, y: 7.0, w: 0.55, h: 0.3, fontSize: 11, color: C.accent5, align: "right" },
  });

  let currentSlide = 0;
  const flatten = (text) => (Array.isArray(text) ? text.map((run) => run.text).join("") : String(text));

  function checkFit(text, w, h, fontSize, charWidth = 0.47) {
    const perLine = Math.max(1, Math.floor((w * 72) / (fontSize * charWidth)));
    let lines = 0;
    for (const para of flatten(text).split("\n")) lines += Math.max(1, Math.ceil(para.length / perLine));
    const needed = (lines * fontSize * 1.2) / 72;
    if (needed > h + 0.02) {
      warnings.push(`${deck.id} slide ${currentSlide}: needs ${needed.toFixed(2)}in, has ${h.toFixed(2)}in: "${flatten(text).slice(0, 50)}"`);
    }
  }

  // The largest size that fits, so text fills its card and stays readable from the back of a room.
  function bestSize(value, w, h, max, min = 14, charWidth = 0.5) {
    for (let size = max; size > min; size -= 1) {
      const perLine = Math.floor((w * 72) / (size * charWidth));
      let lines = 0;
      for (const para of flatten(value).split("\n")) lines += Math.max(1, Math.ceil(para.length / perLine));
      if ((lines * size * 1.25) / 72 <= h) return size;
    }
    return min;
  }

  function text(slide, value, o) {
    const { x, y, w, h, size: fixed, fit, bold = false, color = C.text1, align = "left", valign = "top", italic = false, face, name, spacing } = o;
    const size = fit ? bestSize(value, w, h, fit) : fixed || 14;
    checkFit(value, w, h, size, face === CODE_FONT ? 0.6 : 0.47);
    const options = { x, y, w, h, fontSize: size, bold, italic, color, align, valign, margin: 0, isTextBox: true, objectName: name || "Text" };
    if (face) options.fontFace = face;
    if (spacing) options.paraSpaceAfter = spacing;
    slide.addText(value, options);
  }

  function card(slide, x, y, w, h, fill = C.background2, name = "Card") {
    slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: name });
  }

  function badge(slide, label, x, y, d, scheme, size = 15) {
    slide.addText(String(label), {
      shape: pres.ShapeType.ellipse, x, y, w: d, h: d, fill: { color: scheme.fill }, color: scheme.ink,
      fontSize: size, bold: true, align: "center", valign: "middle", margin: 0, objectName: `Badge ${label}`,
    });
  }

  function arrow(slide, x1, y1, x2, y2, color = C.accent6) {
    slide.addShape(pres.ShapeType.line, {
      x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
      flipH: x2 < x1, flipV: y2 < y1, line: { color, width: 2, endArrowType: "triangle" }, objectName: "Arrow",
    });
  }

  function callout(slide, value, y = 6.1, h = 0.72) {
    card(slide, M, y, CW, h, C.text2, "Key takeaway");
    text(slide, value, { x: M + 0.25, y, w: CW - 0.5, h, size: 16, bold: true, color: C.background1, valign: "middle", name: "Takeaway" });
  }

  // ------------------------------------------------------------- Templates

  const templates = {
    flow(slide, s) {
      const steps = s.steps;
      const bottom = s.takeaway ? 5.85 : BOTTOM;
      const gap = 0.38;
      const w = (CW - gap * (steps.length - 1)) / steps.length;
      const h = bottom - TOP;
      steps.forEach((step, i) => {
        const x = M + i * (w + gap);
        const scheme = colorOf(step, i);
        card(slide, x, TOP, w, h);
        badge(slide, step.badge || i + 1, x + 0.16, TOP + 0.16, 0.5, scheme);
        text(slide, step.title, { x: x + 0.16, y: TOP + 0.76, w: w - 0.3, h: 0.42, size: steps.length > 5 ? 15 : 18, bold: true, color: C.text2 });
        text(slide, step.text, { x: x + 0.16, y: TOP + 1.22, w: w - 0.28, h: h - 1.32, fit: 18 });
        if (i < steps.length - 1) arrow(slide, x + w + 0.03, TOP + h / 2, x + w + gap - 0.03, TOP + h / 2);
      });
      if (s.takeaway) callout(slide, s.takeaway);
    },

    loop(slide, s) {
      const [a, b, c, d] = s.nodes;
      const bw = 2.75, bh = 1.75, gx = 1.25, gy = 1.05;
      const x0 = M, y0 = TOP + 0.02;
      const positions = [[x0, y0], [x0 + bw + gx, y0], [x0 + bw + gx, y0 + bh + gy], [x0, y0 + bh + gy]];
      [a, b, c, d].forEach((node, i) => {
        const [x, y] = positions[i];
        const scheme = colorOf(node, i);
        card(slide, x, y, bw, bh);
        badge(slide, i + 1, x + 0.12, y + 0.12, 0.42, scheme, 14);
        text(slide, node.title, { x: x + 0.62, y: y + 0.14, w: bw - 0.72, h: 0.42, size: 16, bold: true, color: C.text2, valign: "middle" });
        text(slide, node.text, { x: x + 0.14, y: y + 0.64, w: bw - 0.26, h: bh - 0.72, fit: 16 });
      });
      arrow(slide, x0 + bw + 0.06, y0 + bh / 2, x0 + bw + gx - 0.06, y0 + bh / 2);
      arrow(slide, x0 + bw + gx + bw / 2, y0 + bh + 0.06, x0 + bw + gx + bw / 2, y0 + bh + gy - 0.06);
      arrow(slide, x0 + bw + gx - 0.06, y0 + bh + gy + bh / 2, x0 + bw + 0.06, y0 + bh + gy + bh / 2);
      arrow(slide, x0 + bw / 2, y0 + bh + gy - 0.06, x0 + bw / 2, y0 + bh + 0.06);
      const cd = 1.0;
      slide.addText(s.center, {
        shape: pres.ShapeType.ellipse, x: x0 + bw + gx / 2 - cd / 2, y: y0 + bh + gy / 2 - cd / 2, w: cd, h: cd,
        fill: { color: C.accent5 }, color: C.text1, fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0, objectName: "Loop centre",
      });
      const nx = x0 + 2 * bw + gx + 0.45;
      const nw = W - M - nx;
      const count = s.cards.length;
      const nh = (BOTTOM - TOP - 0.2 * (count - 1)) / count;
      s.cards.forEach((note, i) => {
        const y = TOP + i * (nh + 0.2);
        text(slide, note.head, { x: nx, y, w: nw, h: 0.36, size: 18, bold: true, color: C.accent1 });
        text(slide, note.text, { x: nx, y: y + 0.4, w: nw, h: nh - 0.4, fit: 17 });
      });
    },

    layers(slide, s) {
      const rows = s.rows;
      const bottom = s.takeaway ? 5.9 : BOTTOM;
      const gap = 0.12;
      const h = (bottom - TOP - gap * (rows.length - 1)) / rows.length;
      rows.forEach((row, i) => {
        const inset = s.funnel ? i * 0.42 : 0;
        const y = TOP + i * (h + gap);
        const scheme = colorOf(row, i);
        const x = M + inset;
        const w = CW - 2 * inset;
        card(slide, x, y, w, h);
        slide.addText(row.label, {
          shape: pres.ShapeType.roundRect, rectRadius: 0.08, x, y, w: 2.75, h, fill: { color: scheme.fill }, color: scheme.ink,
          fontSize: 16, bold: true, align: "center", valign: "middle", margin: 4, objectName: `Layer ${row.label}`,
        });
        checkFit(row.label, 2.55, h, 16);
        text(slide, row.text, { x: x + 2.95, y, w: w - 3.1, h, fit: 18, valign: "middle" });
      });
      if (s.takeaway) callout(slide, s.takeaway);
    },

    compare(slide, s) {
      const cols = s.cols;
      const bottom = s.takeaway ? 5.9 : BOTTOM;
      const gap = 0.3;
      const w = (CW - gap * (cols.length - 1)) / cols.length;
      cols.forEach((col, i) => {
        const x = M + i * (w + gap);
        const scheme = colorOf(col, i);
        card(slide, x, TOP, w, bottom - TOP);
        slide.addText(col.head, {
          shape: pres.ShapeType.roundRect, rectRadius: 0.08, x, y: TOP, w, h: 0.62, fill: { color: scheme.fill }, color: scheme.ink,
          fontSize: 17, bold: true, align: "center", valign: "middle", margin: 0, objectName: `Column ${col.head}`,
        });
        const body = col.items.map((item, n) => ({ text: item, options: { bullet: { indent: 16 }, breakLine: n < col.items.length - 1, paraSpaceAfter: 9 } }));
        const words = col.items.join("\n");
        const bodyH = bottom - TOP - 0.9 - col.items.length * 0.13;
        const size = bestSize(words, w - 0.56, bodyH, 18);
        checkFit(words, w - 0.56, bodyH, size);
        slide.addText(body, {
          x: x + 0.2, y: TOP + 0.76, w: w - 0.36, h: bottom - TOP - 0.88, fontSize: size, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "Column text",
        });
      });
      if (s.takeaway) callout(slide, s.takeaway);
    },

    cards(slide, s) {
      const items = s.items;
      const cols = s.columns || (items.length > 4 ? 3 : 2);
      const rows = Math.ceil(items.length / cols);
      const bottom = s.takeaway ? 5.85 : BOTTOM;
      const gap = 0.26;
      const w = (CW - gap * (cols - 1)) / cols;
      const h = (bottom - TOP - gap * (rows - 1)) / rows;
      items.forEach((item, i) => {
        const x = M + (i % cols) * (w + gap);
        const y = TOP + Math.floor(i / cols) * (h + gap);
        card(slide, x, y, w, h);
        badge(slide, item.badge || i + 1, x + 0.16, y + 0.16, 0.46, colorOf(item, i), 14);
        text(slide, item.head, { x: x + 0.74, y: y + 0.16, w: w - 0.88, h: 0.46, size: 16, bold: true, color: C.text2, valign: "middle" });
        text(slide, item.text, { x: x + 0.18, y: y + 0.74, w: w - 0.34, h: h - 0.84, fit: 17 });
      });
      if (s.takeaway) callout(slide, s.takeaway);
    },

    hub(slide, s) {
      const bottom = s.takeaway ? 5.85 : BOTTOM;
      const sideW = 3.25;
      const hubW = 3.5;
      const hubX = (W - hubW) / 2;
      const column = (items, x, isInput) => {
        const gap = 0.14;
        const h = (bottom - TOP - gap * (items.length - 1)) / items.length;
        items.forEach((item, i) => {
          const y = TOP + i * (h + gap);
          const scheme = colorOf(item, isInput ? 0 : 1);
          card(slide, x, y, sideW, h);
          const label = item.text ? [{ text: item.title, options: { bold: true, breakLine: true, color: C.text2 } }, { text: item.text }] : item.title;
          text(slide, label, { x: x + 0.18, y, w: sideW - 0.32, h, fit: 16, valign: "middle" });
          void scheme;
          if (isInput) arrow(slide, x + sideW + 0.05, y + h / 2, hubX - 0.05, (TOP + bottom) / 2);
          else arrow(slide, hubX + hubW + 0.05, (TOP + bottom) / 2, x - 0.05, y + h / 2);
        });
      };
      column(s.inputs, M, true);
      column(s.outputs, W - M - sideW, false);
      card(slide, hubX, TOP + 0.35, hubW, bottom - TOP - 0.7, C.accent1, "Hub");
      text(slide, s.hub.title, { x: hubX + 0.22, y: TOP + 0.6, w: hubW - 0.44, h: 0.8, size: 20, bold: true, color: C.background1, align: "center", valign: "middle" });
      text(slide, s.hub.text, { x: hubX + 0.25, y: TOP + 1.45, w: hubW - 0.5, h: bottom - TOP - 2.0, fit: 20, color: C.background1, align: "center" });
      if (s.takeaway) callout(slide, s.takeaway);
    },

    chart(slide, s) {
      const charts = s.charts;
      const bottom = s.takeaway ? 5.85 : BOTTOM;
      const notesW = s.cards ? 3.5 : 0;
      const areaW = CW - (notesW ? notesW + 0.3 : 0);
      const gap = 0.25;
      const w = (areaW - gap * (charts.length - 1)) / charts.length;
      charts.forEach((chart, i) => {
        const x = M + i * (w + gap);
        slide.addChart(pres.ChartType.bar, [{ name: chart.title, labels: chart.labels, values: chart.values }], {
          x, y: TOP, w, h: bottom - TOP,
          barDir: "bar", barGapWidthPct: 45, chartColors: [THEME.colors.accent1],
          showTitle: true, title: chart.title, titleFontFace: "+mn-lt", titleFontSize: 15, titleColor: THEME.colors.dk2,
          showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelFontFace: "+mn-lt", dataLabelFontSize: 13,
          dataLabelColor: THEME.colors.dk1, dataLabelFormatCode: chart.format || "General",
          catAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 13, catAxisLabelColor: THEME.colors.dk1, catAxisOrientation: "maxMin",
          valAxisHidden: true, valAxisLabelFontSize: 11, valGridLine: { style: "none" }, catGridLine: { style: "none" },
          valAxisMinVal: 0, valAxisMaxVal: chart.max,
          altText: `${chart.title}: ${chart.labels.map((label, n) => `${label} ${chart.values[n]}`).join(", ")}`,
          objectName: `Chart ${chart.title}`,
        });
      });
      if (s.cards) {
        const nx = M + areaW + 0.3;
        const nh = (bottom - TOP - 0.2 * (s.cards.length - 1)) / s.cards.length;
        s.cards.forEach((note, i) => {
          const y = TOP + i * (nh + 0.2);
          card(slide, nx, y, notesW, nh);
          text(slide, note.head, { x: nx + 0.16, y: y + 0.1, w: notesW - 0.3, h: 0.34, size: 16, bold: true, color: C.accent1 });
          text(slide, note.text, { x: nx + 0.16, y: y + 0.46, w: notesW - 0.3, h: nh - 0.54, fit: 16 });
        });
      }
      if (s.takeaway) callout(slide, s.takeaway);
    },

    code(slide, s) {
      const panelW = 7.75;
      const h = BOTTOM - TOP;
      card(slide, M, TOP, panelW, h, C.text1, "Code panel");
      const lines = s.code.split("\n");
      lines.forEach((line) => {
        if (line.length > 60) warnings.push(`${deck.id} slide ${currentSlide}: code line too long (${line.length}): ${line}`);
      });
      const longest = Math.max(...lines.map((line) => line.length));
      const codeSize = Math.min(19, Math.floor(((panelW - 0.4) * 72) / (0.6 * longest)), Math.floor(((h - 0.4) * 72) / (1.2 * lines.length)));
      if (codeSize < 14) warnings.push(`${deck.id} slide ${currentSlide}: code would shrink to ${codeSize}pt`);
      slide.addText(s.code, {
        x: M + 0.22, y: TOP + 0.2, w: panelW - 0.4, h: h - 0.4, fontFace: CODE_FONT, fontSize: Math.max(codeSize, 14), color: C.accent5,
        valign: "top", margin: 0, isTextBox: true, objectName: "Code",
      });
      const nx = M + panelW + 0.3;
      const nw = W - M - nx;
      const nh = (h - 0.2 * (s.points.length - 1)) / s.points.length;
      s.points.forEach((point, i) => {
        const y = TOP + i * (nh + 0.2);
        card(slide, nx, y, nw, nh);
        text(slide, point.head, { x: nx + 0.16, y: y + 0.1, w: nw - 0.3, h: 0.34, size: 17, bold: true, color: C.accent1 });
        text(slide, point.text, { x: nx + 0.16, y: y + 0.48, w: nw - 0.3, h: nh - 0.56, fit: 17 });
      });
    },

    app(slide, s) {
      const steps = s.steps;
      const stripH = 0.42 * s.commands.length + 0.3;
      const bottom = BOTTOM - stripH - 0.22;
      const gap = 0.38;
      const w = (CW - gap * (steps.length - 1)) / steps.length;
      const h = bottom - TOP;
      steps.forEach((step, i) => {
        const x = M + i * (w + gap);
        const scheme = colorOf(step, i);
        card(slide, x, TOP, w, h);
        slide.addText(step.title, {
          shape: pres.ShapeType.roundRect, rectRadius: 0.08, x, y: TOP, w, h: 0.6, fill: { color: scheme.fill }, color: scheme.ink,
          fontSize: 15, bold: true, align: "center", valign: "middle", margin: 2, objectName: `Stage ${step.title}`,
        });
        checkFit(step.title, w - 0.1, 0.6, 15);
        text(slide, step.text, { x: x + 0.14, y: TOP + 0.74, w: w - 0.26, h: h - 0.84, fit: 18 });
        if (i < steps.length - 1) arrow(slide, x + w + 0.03, TOP + h / 2, x + w + gap - 0.03, TOP + h / 2);
      });
      card(slide, M, BOTTOM - stripH, CW, stripH, C.text1, "Run commands");
      s.commands.forEach((command, i) => {
        if (command.length > 94) warnings.push(`${deck.id} slide ${currentSlide}: command too long (${command.length}): ${command}`);
        text(slide, command, { x: M + 0.22, y: BOTTOM - stripH + 0.15 + i * 0.42, w: CW - 0.4, h: 0.38, size: 14, face: CODE_FONT, color: C.accent5, valign: "middle", name: "Command" });
      });
    },

    checklist(slide, s) {
      const items = s.items;
      const rows = Math.ceil(items.length / 2);
      const gap = 0.2;
      const w = (CW - 0.35) / 2;
      const h = (BOTTOM - TOP - gap * (rows - 1)) / rows;
      items.forEach((item, i) => {
        const x = M + (i % 2) * (w + 0.35);
        const y = TOP + Math.floor(i / 2) * (h + gap);
        card(slide, x, y, w, h);
        badge(slide, "✓", x + 0.16, y + (h - 0.46) / 2, 0.46, COLORS.teal, 16);
        text(slide, [{ text: item.head, options: { bold: true, color: C.text2, breakLine: true } }, { text: item.text }], { x: x + 0.78, y, w: w - 0.92, h, fit: 17, valign: "middle" });
      });
    },

    statement(slide, s) {
      const leftW = 5.3;
      card(slide, M, TOP, leftW, BOTTOM - TOP, C.text2, "Big idea");
      text(slide, s.big, { x: M + 0.35, y: TOP + 0.35, w: leftW - 0.7, h: 2.9, size: 28, bold: true, color: C.background1 });
      text(slide, s.sub, { x: M + 0.35, y: TOP + 3.35, w: leftW - 0.7, h: 1.7, size: 16, color: C.accent5 });
      const x = M + leftW + 0.35;
      const w = W - M - x;
      const gap = 0.2;
      const h = (BOTTOM - TOP - gap * (s.items.length - 1)) / s.items.length;
      s.items.forEach((item, i) => {
        const y = TOP + i * (h + gap);
        card(slide, x, y, w, h);
        badge(slide, item.badge || i + 1, x + 0.18, y + (h - 0.54) / 2, 0.54, colorOf(item, i));
        text(slide, [{ text: item.head, options: { bold: true, color: C.text2, breakLine: true } }, { text: item.text }], { x: x + 0.9, y, w: w - 1.05, h, fit: 18, valign: "middle" });
      });
    },

    dodont(slide, s) {
      const gap = 0.35;
      const w = (CW - gap) / 2;
      const col = (x, head, scheme, items, mark) => {
        slide.addText(head, {
          shape: pres.ShapeType.roundRect, rectRadius: 0.08, x, y: TOP, w, h: 0.56, fill: { color: scheme.fill }, color: scheme.ink,
          fontSize: 17, bold: true, align: "center", valign: "middle", margin: 0, objectName: head,
        });
        const top = TOP + 0.68;
        const g = 0.14;
        const h = (BOTTOM - top - g * (items.length - 1)) / items.length;
        items.forEach((item, i) => {
          const y = top + i * (h + g);
          card(slide, x, y, w, h);
          badge(slide, mark, x + 0.14, y + (h - 0.38) / 2, 0.38, scheme, 13);
          text(slide, item, { x: x + 0.64, y, w: w - 0.78, h, fit: 18, valign: "middle" });
        });
      };
      col(M, "Common mistakes", COLORS.coral, s.dont, "✕");
      col(M + w + gap, "What professionals do", COLORS.teal, s.do, "✓");
    },
  };

  // ------------------------------------------------------------- Title and closing slides

  function titleSlide() {
    currentSlide += 1;
    pres.addSection({ title: "Introduction" });
    const slide = pres.addSlide({ masterName: "DARK", sectionTitle: "Introduction" });
    text(slide, deck.module.toUpperCase(), { x: M, y: 0.32, w: CW, h: 0.3, size: 14, bold: true, color: C.accent5, name: "Module" });
    checkFit(deck.title, CW, 1.35, 40, 0.5);
    slide.addText(deck.title, { placeholder: "title" });
    const oneLine = deck.title.length <= 40;
    const subY = oneLine ? 1.42 : 2.02;
    text(slide, deck.subtitle, { x: M, y: subY, w: CW, h: 0.45, size: 20, color: C.accent5, name: "Subtitle" });
    const cardY = subY + 0.72;
    const cardH = 5.6 - cardY;
    const gap = 0.3;
    const w = (CW - gap * 2) / 3;
    deck.outcomes.forEach((outcome, i) => {
      const x = M + i * (w + gap);
      card(slide, x, cardY, w, cardH, C.accent1, "Outcome");
      badge(slide, i + 1, x + 0.2, cardY + 0.2, 0.5, COLORS.mint, 16);
      text(slide, outcome, { x: x + 0.22, y: cardY + 0.84, w: w - 0.42, h: cardH - 0.95, fit: 20, color: C.background1, name: "Outcome text" });
    });
    text(slide, [{ text: "You will build:  ", options: { bold: true, color: C.accent5 } }, { text: deck.build, options: { color: C.background1 } }], { x: M, y: 5.85, w: CW, h: 0.8, size: 20, name: "Build" });
    slide.addNotes(deck.notes);
  }

  function labSlide(s) {
    currentSlide += 1;
    pres.addSection({ title: "Lab" });
    const slide = pres.addSlide({ masterName: "DARK", sectionTitle: "Lab" });
    checkFit(s.title, CW, 1.35, 40, 0.5);
    slide.addText(s.title, { placeholder: "title" });
    const gap = 0.2;
    const top = 1.75;
    const h = (6.0 - top - gap * (s.steps.length - 1)) / s.steps.length;
    s.steps.forEach((step, i) => {
      const y = top + i * (h + gap);
      card(slide, M, y, CW, h, C.accent1, "Lab step");
      badge(slide, i + 1, M + 0.18, y + (h - 0.5) / 2, 0.5, COLORS.mint);
      text(slide, step, { x: M + 0.9, y, w: CW - 1.1, h, fit: 20, color: C.background1, valign: "middle", name: "Lab step text" });
    });
    text(slide, s.next, { x: M, y: 6.2, w: 11.2, h: 0.65, size: 16, color: C.accent5, valign: "middle", name: "Next" });
    slide.addNotes(s.notes);
  }

  titleSlide();
  pres.addSection({ title: "Concepts" });
  for (const s of deck.slides) {
    if (s.type === "lab") {
      labSlide(s);
      continue;
    }
    currentSlide += 1;
    const slide = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Concepts" });
    if (s.title.length > 110) warnings.push(`${deck.id} slide ${currentSlide}: title long (${s.title.length})`);
    checkFit(s.title, CW, 1.0, 28, 0.5);
    slide.addText(s.title, { placeholder: "title" });
    // Slide data: "notes" is either the talk track, or the on-slide cards when "speaker" holds the talk track.
    const cards = Array.isArray(s.notes) ? s.notes : undefined;
    templates[s.type](slide, { ...s, cards });
    slide.addNotes(s.speaker || s.notes);
  }
  return pres;
}

async function writeDeck(deck, path) {
  const pres = buildDeck(deck);
  await pres.writeFile({ fileName: path });
  await applyTheme(path, THEME);
}

module.exports = { writeDeck, warnings };
