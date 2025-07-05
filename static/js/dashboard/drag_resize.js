import { saveDashboardState } from './save.js';

export function makeDraggableAndResizable(target, chartInstance) {
  // Set initial z-index based on existing widgets
  const existingWidgets = document.querySelectorAll('.chart-widget').length;
  target.style.zIndex = 10 + existingWidgets;
  
  // Track the highest z-index to ensure new widgets stack properly
  let highestZIndex = 10 + existingWidgets;
  
  interact(target)
    .draggable({
      inertia: true,
      modifiers: [
        interact.modifiers.restrictRect({
          restriction: 'parent',
          endOnly: true
        })
      ],
      listeners: {
        start: function(event) {
          // Find the current highest z-index among all widgets
          const widgets = document.querySelectorAll('.chart-widget');
          highestZIndex = Math.max(...Array.from(widgets).map(w => 
            parseInt(window.getComputedStyle(w).zIndex) || 10
          ));
          
          // Set this widget to be on top
          event.target.style.zIndex = highestZIndex + 1;
          event.target.classList.add('active-widget');
        },
        move: function(event) {
          const x = (parseFloat(target.dataset.x) || 0) + event.dx;
          const y = (parseFloat(target.dataset.y) || 0) + event.dy;

          // Update actual position, not transform
          target.style.left = `${x}px`;
          target.style.top = `${y}px`;
          target.dataset.x = x;
          target.dataset.y = y;
        },
        end: function(event) {
          // Keep the widget on top after dragging
          event.target.style.zIndex = highestZIndex + 1;
          event.target.classList.remove('active-widget');
          saveDashboardState();
        }
      }
    })
    .resizable({
      edges: { left: true, right: true, bottom: true, top: true },
      listeners: {
        start: function(event) {
          event.target.classList.add('active-widget');
        },
        move: function(event) {
          // Update size and position
          event.target.style.width = `${event.rect.width}px`;
          event.target.style.height = `${event.rect.height}px`;
          event.target.style.left = `${parseFloat(event.target.dataset.x) + event.deltaRect.left}px`;
          event.target.style.top = `${parseFloat(event.target.dataset.y) + event.deltaRect.top}px`;
          
          if (chartInstance?.resize) {
            chartInstance.resize();
          }
        },
        end: function(event) {
          event.target.classList.remove('active-widget');
          
          saveDashboardState();
        }
      },
      modifiers: [
        interact.modifiers.restrictSize({
          min: { width: 150, height: 100 }
        })
      ],
      inertia: true
    });
}