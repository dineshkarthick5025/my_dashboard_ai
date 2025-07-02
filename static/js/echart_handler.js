function renderEChart(configJson) {
  const chartId = `chart_${Date.now()}`;
  const chartDiv = document.createElement("div");
  chartDiv.id = chartId;
  chartDiv.className = "echart-box";
  chartDiv.style.width = "400px";
  chartDiv.style.height = "300px";
  chartDiv.style.position = "absolute";
  chartDiv.style.border = "1px solid #ccc";
  chartDiv.style.background = "#fff";
  chartDiv.style.left = "50px";
  chartDiv.style.top = "50px";
  chartDiv.style.resize = "both";
  chartDiv.style.overflow = "hidden";

  document.getElementById("dashboardCanvas").appendChild(chartDiv);

  const myChart = echarts.init(chartDiv);
  myChart.setOption(configJson);

  interact(`#${chartId}`)
    .draggable({
      listeners: {
        move(event) {
          const target = event.target;
          const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
          const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

          target.style.transform = `translate(${x}px, ${y}px)`;
          target.setAttribute('data-x', x);
          target.setAttribute('data-y', y);
        }
      }
    })
    .resizable({
      edges: { left: true, right: true, bottom: true, top: true },
      listeners: {
        move(event) {
          let { x, y } = event.target.dataset;
          x = parseFloat(x) || 0;
          y = parseFloat(y) || 0;

          Object.assign(event.target.style, {
            width: `${event.rect.width}px`,
            height: `${event.rect.height}px`
          });

          const dx = event.deltaRect.left;
          const dy = event.deltaRect.top;

          x += dx;
          y += dy;

          event.target.style.transform = `translate(${x}px, ${y}px)`;
          event.target.setAttribute('data-x', x);
          event.target.setAttribute('data-y', y);

          echarts.getInstanceByDom(event.target)?.resize();
        }
      }
    });
}
