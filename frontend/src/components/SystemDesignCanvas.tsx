import React, { useRef, useEffect, useState, useCallback } from 'react';

interface SystemDesignCanvasProps {
  onScreenshot: (imageData: string) => void;
  onProgressUpdate: (progress: any) => void;
  questionText: string;
}

interface DrawingTool {
  type: 'select' | 'rectangle' | 'circle' | 'arrow';
  label: string;
  icon: string;
}

interface CanvasObject {
  id: string;
  type: 'rectangle' | 'circle' | 'arrow';
  x: number;
  y: number;
  width?: number;
  height?: number;
  radius?: number;
  text?: string;
  color: string;
  isSelected?: boolean;
}

const SystemDesignCanvas: React.FC<SystemDesignCanvasProps> = ({
  onScreenshot,
  onProgressUpdate,
  questionText
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedTool, setSelectedTool] = useState<DrawingTool['type']>('select');
  const [canvasObjects, setCanvasObjects] = useState<CanvasObject[]>([]);
  const [lastScreenshot, setLastScreenshot] = useState<number>(0);
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
  const [selectedObject, setSelectedObject] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number } | null>(null);
  const [showTextInput, setShowTextInput] = useState(false);
  const [textInputPosition, setTextInputPosition] = useState<{ x: number; y: number } | null>(null);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeHandle, setResizeHandle] = useState<string | null>(null);
  const [resizeStartData, setResizeStartData] = useState<{ x: number; y: number; width: number; height: number; radius: number } | null>(null);

  const tools: DrawingTool[] = [
    { type: 'select', label: 'Select', icon: '↖️' },
    { type: 'rectangle', label: 'Rectangle', icon: '⬜' },
    { type: 'circle', label: 'Circle', icon: '⭕' },
    { type: 'arrow', label: 'Arrow', icon: '➡️' }
  ];

  // Screenshot every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (canvasRef.current) {
        const imageData = canvasRef.current.toDataURL('image/png');
        onScreenshot(imageData);
        setLastScreenshot(Date.now());
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [onScreenshot]);

  // Progress update every minute
  useEffect(() => {
    const interval = setInterval(() => {
      const progress = {
        timestamp: Date.now(),
        objectCount: canvasObjects.length,
        objects: canvasObjects,
      };
      onProgressUpdate(progress);
    }, 60000); // Every minute

    return () => clearInterval(interval);
  }, [onProgressUpdate, canvasObjects]);

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw all objects
    canvasObjects.forEach(obj => {
      const isSelected = obj.id === selectedObject;
      
      ctx.strokeStyle = isSelected ? '#ff6b6b' : obj.color;
      ctx.fillStyle = obj.color;
      ctx.lineWidth = isSelected ? 3 : 2;

      switch (obj.type) {
        case 'rectangle':
          ctx.strokeRect(obj.x, obj.y, obj.width || 100, obj.height || 50);
          if (isSelected) {
            // Draw selection handles
            ctx.fillStyle = '#ff6b6b';
            ctx.fillRect(obj.x - 5, obj.y - 5, 10, 10);
            ctx.fillRect(obj.x + (obj.width || 100) - 5, obj.y - 5, 10, 10);
            ctx.fillRect(obj.x - 5, obj.y + (obj.height || 50) - 5, 10, 10);
            ctx.fillRect(obj.x + (obj.width || 100) - 5, obj.y + (obj.height || 50) - 5, 10, 10);
          }
          
          // Draw text if it exists
          if (obj.text) {
            ctx.fillStyle = '#333333';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(obj.text, obj.x + (obj.width || 100) / 2, obj.y + (obj.height || 50) / 2 + 5);
            ctx.textAlign = 'left';
          }
          break;
        case 'circle':
          ctx.beginPath();
          ctx.arc(obj.x, obj.y, obj.radius || 25, 0, 2 * Math.PI);
          ctx.stroke();
          if (isSelected) {
            // Draw selection handles
            ctx.fillStyle = '#ff6b6b';
            ctx.fillRect(obj.x - (obj.radius || 25) - 5, obj.y - 5, 10, 10);
            ctx.fillRect(obj.x + (obj.radius || 25) - 5, obj.y - 5, 10, 10);
            ctx.fillRect(obj.x - 5, obj.y - (obj.radius || 25) - 5, 10, 10);
            ctx.fillRect(obj.x - 5, obj.y + (obj.radius || 25) - 5, 10, 10);
          }
          
          // Draw text if it exists
          if (obj.text) {
            ctx.fillStyle = '#333333';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(obj.text, obj.x, obj.y + 5);
            ctx.textAlign = 'left';
          }
          break;
        case 'arrow':
          // Draw arrow line
          ctx.beginPath();
          ctx.moveTo(obj.x, obj.y);
          ctx.lineTo(obj.x + (obj.width || 50), obj.y + (obj.height || 0));
          ctx.stroke();
          
          // Draw arrowhead
          const angle = Math.atan2((obj.height || 0), (obj.width || 50));
          const arrowLength = 15;
          const arrowAngle = Math.PI / 6;
          
          ctx.beginPath();
          ctx.moveTo(obj.x + (obj.width || 50), obj.y + (obj.height || 0));
          ctx.lineTo(
            obj.x + (obj.width || 50) - arrowLength * Math.cos(angle - arrowAngle),
            obj.y + (obj.height || 0) - arrowLength * Math.sin(angle - arrowAngle)
          );
          ctx.moveTo(obj.x + (obj.width || 50), obj.y + (obj.height || 0));
          ctx.lineTo(
            obj.x + (obj.width || 50) - arrowLength * Math.cos(angle + arrowAngle),
            obj.y + (obj.height || 0) - arrowLength * Math.sin(angle + arrowAngle)
          );
          ctx.stroke();
          
          if (isSelected) {
            // Draw selection handles
            ctx.fillStyle = '#ff6b6b';
            ctx.fillRect(obj.x - 5, obj.y - 5, 10, 10);
            ctx.fillRect(obj.x + (obj.width || 50) - 5, obj.y + (obj.height || 0) - 5, 10, 10);
          }
          break;
      }
    });
  }, [canvasObjects]);

  useEffect(() => {
    drawCanvas();
  }, [drawCanvas]);

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (selectedTool === 'select') {
      // First check if clicking on a resize handle
      if (selectedObject) {
        const selectedObj = canvasObjects.find(obj => obj.id === selectedObject);
        if (selectedObj) {
          const handle = getResizeHandle(selectedObj, x, y);
          if (handle) {
            setIsResizing(true);
            setResizeHandle(handle);
            setResizeStartData({
              x: selectedObj.x,
              y: selectedObj.y,
              width: selectedObj.width || 100,
              height: selectedObj.height || 50,
              radius: selectedObj.radius || 25
            });
            return;
          }
        }
      }

      // Check if clicking on an object
      const clickedObject = canvasObjects.find(obj => {
        if (obj.type === 'rectangle') {
          return x >= obj.x && x <= obj.x + (obj.width || 100) && 
                 y >= obj.y && y <= obj.y + (obj.height || 50);
        } else if (obj.type === 'circle') {
          const distance = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
          return distance <= (obj.radius || 25);
        } else if (obj.type === 'arrow') {
          // Check if click is near the arrow line
          const lineLength = Math.sqrt((obj.width || 50) ** 2 + (obj.height || 0) ** 2);
          const clickToStart = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
          const clickToEnd = Math.sqrt((x - (obj.x + (obj.width || 50))) ** 2 + (y - (obj.y + (obj.height || 0))) ** 2);
          return Math.abs(clickToStart + clickToEnd - lineLength) < 10;
        }
        return false;
      });

      if (clickedObject) {
        setSelectedObject(clickedObject.id);
        setIsDragging(true);
        setDragOffset({ x: x - clickedObject.x, y: y - clickedObject.y });
      } else {
        setSelectedObject(null);
      }
    } else if (selectedTool !== 'select') {
      setIsDrawing(true);
      setStartPoint({ x, y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (isResizing && selectedObject && resizeHandle && resizeStartData) {
      // Handle resizing
      setCanvasObjects(prev => prev.map(obj => {
        if (obj.id !== selectedObject) return obj;
        
        const newObj = { ...obj };
        
        if (obj.type === 'rectangle') {
          switch (resizeHandle) {
            case 'nw': // top-left
              newObj.width = resizeStartData.width + (resizeStartData.x - x);
              newObj.height = resizeStartData.height + (resizeStartData.y - y);
              newObj.x = x;
              newObj.y = y;
              break;
            case 'ne': // top-right
              newObj.width = x - resizeStartData.x;
              newObj.height = resizeStartData.height + (resizeStartData.y - y);
              newObj.y = y;
              break;
            case 'sw': // bottom-left
              newObj.width = resizeStartData.width + (resizeStartData.x - x);
              newObj.height = y - resizeStartData.y;
              newObj.x = x;
              break;
            case 'se': // bottom-right
              newObj.width = x - resizeStartData.x;
              newObj.height = y - resizeStartData.y;
              break;
          }
        } else if (obj.type === 'circle') {
          if (resizeHandle === 'resize') {
            const newRadius = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
            newObj.radius = Math.max(10, newRadius); // Minimum radius of 10
          }
        } else if (obj.type === 'arrow') {
          if (resizeHandle === 'resize') {
            newObj.width = x - resizeStartData.x;
            newObj.height = y - resizeStartData.y;
          }
        }
        
        return newObj;
      }));
    } else if (isDragging && selectedObject && dragOffset) {
      // Handle dragging
      setCanvasObjects(prev => prev.map(obj => 
        obj.id === selectedObject 
          ? { ...obj, x: x - dragOffset.x, y: y - dragOffset.y }
          : obj
      ));
    }
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isResizing) {
      setIsResizing(false);
      setResizeHandle(null);
      setResizeStartData(null);
      return;
    }

    if (isDragging) {
      setIsDragging(false);
      setDragOffset(null);
      return;
    }

    if (!isDrawing || !startPoint) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newObject: CanvasObject = {
      id: Date.now().toString(),
      type: selectedTool as 'rectangle' | 'circle' | 'arrow',
      x: startPoint.x,
      y: startPoint.y,
      width: x - startPoint.x,
      height: y - startPoint.y,
      color: selectedTool === 'rectangle' ? '#1976d2' : 
             selectedTool === 'circle' ? '#7b1fa2' : 
             selectedTool === 'arrow' ? '#ff6b6b' : '#333333'
    };

    if (selectedTool === 'circle') {
      newObject.radius = Math.abs(x - startPoint.x) / 2;
      newObject.x = startPoint.x + newObject.radius;
      newObject.y = startPoint.y + newObject.radius;
    }

    setCanvasObjects(prev => [...prev, newObject]);
    setIsDrawing(false);
    setStartPoint(null);
  };

  const handleDoubleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (selectedTool !== 'select') return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if double-clicking on an object
    const clickedObject = canvasObjects.find(obj => {
      if (obj.type === 'rectangle') {
        return x >= obj.x && x <= obj.x + (obj.width || 100) && 
               y >= obj.y && y <= obj.y + (obj.height || 50);
      } else if (obj.type === 'circle') {
        const distance = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
        return distance <= (obj.radius || 25);
      } else if (obj.type === 'arrow') {
        const lineLength = Math.sqrt((obj.width || 50) ** 2 + (obj.height || 0) ** 2);
        const clickToStart = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
        const clickToEnd = Math.sqrt((x - (obj.x + (obj.width || 50))) ** 2 + (y - (obj.y + (obj.height || 0))) ** 2);
        return Math.abs(clickToStart + clickToEnd - lineLength) < 10;
      }
      return false;
    });

    if (clickedObject) {
      handleObjectDoubleClick(clickedObject.id, x, y);
    }
  };

  const clearCanvas = () => {
    setCanvasObjects([]);
    setSelectedObject(null);
  };

  const undo = () => {
    setCanvasObjects(prev => prev.slice(0, -1));
    setSelectedObject(null);
  };

  const deleteSelected = () => {
    if (selectedObject) {
      setCanvasObjects(prev => prev.filter(obj => obj.id !== selectedObject));
      setSelectedObject(null);
    }
  };

  const addTextToObject = (objectId: string, text: string) => {
    setCanvasObjects(prev => prev.map(obj => 
      obj.id === objectId 
        ? { ...obj, text: text || obj.text }
        : obj
    ));
    setShowTextInput(false);
    setTextInputPosition(null);
  };

  const handleObjectDoubleClick = (objectId: string, x: number, y: number) => {
    setSelectedObject(objectId);
    setTextInputPosition({ x, y });
    setShowTextInput(true);
  };

  const getResizeHandle = (object: CanvasObject, x: number, y: number): string | null => {
    const handleSize = 8;
    const margin = 5;
    
    if (object.type === 'rectangle') {
      const width = object.width || 100;
      const height = object.height || 50;
      
      // Top-left corner
      if (x >= object.x - margin && x <= object.x + handleSize + margin &&
          y >= object.y - margin && y <= object.y + handleSize + margin) {
        return 'nw';
      }
      // Top-right corner
      if (x >= object.x + width - handleSize - margin && x <= object.x + width + margin &&
          y >= object.y - margin && y <= object.y + handleSize + margin) {
        return 'ne';
      }
      // Bottom-left corner
      if (x >= object.x - margin && x <= object.x + handleSize + margin &&
          y >= object.y + height - handleSize - margin && y <= object.y + height + margin) {
        return 'sw';
      }
      // Bottom-right corner
      if (x >= object.x + width - handleSize - margin && x <= object.x + width + margin &&
          y >= object.y + height - handleSize - margin && y <= object.y + height + margin) {
        return 'se';
      }
    } else if (object.type === 'circle') {
      const radius = object.radius || 25;
      const distance = Math.sqrt((x - object.x) ** 2 + (y - object.y) ** 2);
      if (distance >= radius - handleSize && distance <= radius + handleSize) {
        return 'resize';
      }
    } else if (object.type === 'arrow') {
      // Arrows can be resized by dragging the end point
      const endX = object.x + (object.width || 50);
      const endY = object.y + (object.height || 0);
      const distance = Math.sqrt((x - endX) ** 2 + (y - endY) ** 2);
      if (distance <= handleSize + margin) {
        return 'resize';
      }
    }
    
    return null;
  };

  const drawResizeHandles = (ctx: CanvasRenderingContext2D, object: CanvasObject) => {
    if (!selectedObject || selectedObject !== object.id) return;
    
    ctx.save();
    ctx.fillStyle = '#1976d2';
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    
    if (object.type === 'rectangle') {
      const width = object.width || 100;
      const height = object.height || 50;
      const handleSize = 8;
      
      // Draw corner handles
      const handles = [
        { x: object.x, y: object.y }, // top-left
        { x: object.x + width, y: object.y }, // top-right
        { x: object.x, y: object.y + height }, // bottom-left
        { x: object.x + width, y: object.y + height }, // bottom-right
      ];
      
      handles.forEach(handle => {
        ctx.fillRect(handle.x - handleSize/2, handle.y - handleSize/2, handleSize, handleSize);
        ctx.strokeRect(handle.x - handleSize/2, handle.y - handleSize/2, handleSize, handleSize);
      });
    } else if (object.type === 'circle') {
      const radius = object.radius || 25;
      const handleSize = 8;
      
      // Draw resize handle on the right edge
      const handleX = object.x + radius;
      const handleY = object.y;
      
      ctx.fillRect(handleX - handleSize/2, handleY - handleSize/2, handleSize, handleSize);
      ctx.strokeRect(handleX - handleSize/2, handleY - handleSize/2, handleSize, handleSize);
    } else if (object.type === 'arrow') {
      const handleSize = 8;
      
      // Draw resize handle at the end of the arrow
      const endX = object.x + (object.width || 50);
      const endY = object.y + (object.height || 0);
      
      ctx.fillRect(endX - handleSize/2, endY - handleSize/2, handleSize, handleSize);
      ctx.strokeRect(endX - handleSize/2, endY - handleSize/2, handleSize, handleSize);
    }
    
    ctx.restore();
  };

  const resetCanvas = () => {
    setCanvasObjects([]);
    setSelectedObject(null);
    setIsDrawing(false);
    setStartPoint(null);
    setIsDragging(false);
    setDragOffset(null);
  };

  // Reset canvas when question changes
  useEffect(() => {
    resetCanvas();
  }, [questionText]);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        deleteSelected();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedObject]);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header with question */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">System Design Question</h3>
        <p className="text-gray-600 text-sm">{questionText}</p>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-2 p-3 border-b border-gray-200 bg-gray-50">
        {tools.map((tool) => (
          <button
            key={tool.type}
            onClick={() => setSelectedTool(tool.type)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedTool === tool.type
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            <span>{tool.icon}</span>
            <span>{tool.label}</span>
          </button>
        ))}
        
        <div className="flex-1" />
        
        <button
          onClick={undo}
          className="px-3 py-2 bg-gray-500 text-white rounded-lg text-sm font-medium hover:bg-gray-600 transition-colors"
        >
          ↶ Undo
        </button>
        
        <button
          onClick={deleteSelected}
          disabled={!selectedObject}
          className="px-3 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          🗑️ Delete
        </button>
        
        <button
          onClick={clearCanvas}
          className="px-3 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors"
        >
          🧹 Clear All
        </button>
      </div>

      {/* Canvas */}
      <div className="flex-1 p-4">
        <div className="w-full h-full border border-gray-300 rounded-lg overflow-hidden relative">
          <canvas
            ref={canvasRef}
            width={800}
            height={600}
            className={`w-full h-full ${
              isResizing 
                ? 'cursor-nw-resize' 
                : selectedTool === 'select' 
                  ? 'cursor-pointer' 
                  : 'cursor-crosshair'
            }`}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onDoubleClick={handleDoubleClick}
            tabIndex={0}
          />
          
          {/* Text Input Overlay */}
          {showTextInput && textInputPosition && (
            <div
              className="absolute bg-white border border-gray-300 rounded shadow-lg p-2 z-10"
              style={{
                left: textInputPosition.x,
                top: textInputPosition.y,
              }}
            >
              <input
                type="text"
                placeholder="Enter text..."
                className="w-32 px-2 py-1 border border-gray-300 rounded text-sm"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && selectedObject) {
                    addTextToObject(selectedObject, e.currentTarget.value);
                  } else if (e.key === 'Escape') {
                    setShowTextInput(false);
                    setTextInputPosition(null);
                  }
                }}
                onBlur={() => {
                  setShowTextInput(false);
                  setTextInputPosition(null);
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between p-3 border-t border-gray-200 bg-gray-50 text-sm text-gray-600">
        <div>
          Objects: {canvasObjects.length} | Tool: {tools.find(t => t.type === selectedTool)?.label}
          {selectedObject && <span className="ml-2 text-blue-600">• Selected</span>}
        </div>
        <div className="text-xs">
          <div>Last screenshot: {lastScreenshot ? new Date(lastScreenshot).toLocaleTimeString() : 'Never'}</div>
          <div className="text-gray-500">
            Press Delete to remove selected object • Double-click object to add text • Drag corners to resize
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemDesignCanvas;