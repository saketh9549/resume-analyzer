import React, { useState } from "react"
import { motion } from "framer-motion"
import { X, ZoomIn, ZoomOut, Download, Maximize2, Minimize2 } from "lucide-react"

function ResumePreviewModal({ isOpen, onClose, fileUrl, fileName, onDownload }) {
  const [zoom, setZoom] = useState(100)
  const [isFullscreen, setIsFullscreen] = useState(false)

  if (!isOpen) return null

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 20, 200))
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 20, 60))
  const toggleFullscreen = () => setIsFullscreen(!isFullscreen)

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-md z-[9999] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        className={`bg-slate-900 border border-white/10 w-full rounded-3xl flex flex-col justify-between shadow-2xl relative transition-all duration-300 ${
          isFullscreen ? "h-[96vh] max-w-[96vw]" : "h-[85vh] max-w-4xl"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-slate-950/40 rounded-t-3xl shrink-0">
          <div className="flex-1 min-w-0 pr-4">
            <h3 className="text-lg font-bold text-gray-100 truncate">Resume Live Preview</h3>
            <p className="text-xs text-gray-400 truncate mt-0.5">{fileName}</p>
          </div>
          
          {/* Controls */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleZoomOut}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut size={15} />
            </button>
            <span className="text-xs text-gray-400 w-10 text-center font-mono font-semibold">
              {zoom}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn size={15} />
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition cursor-pointer ml-1"
              title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            >
              {isFullscreen ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
            </button>
            
            <button
              onClick={onDownload}
              className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 hover:bg-blue-500/20 transition cursor-pointer"
              title="Download PDF"
            >
              <Download size={15} />
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 transition cursor-pointer ml-2 border border-white/5"
              title="Close"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        {/* PDF Frame Viewer */}
        <div className="flex-1 bg-slate-950 overflow-hidden relative">
          <div 
            className="w-full h-full transition-transform duration-200 origin-top"
            style={{ transform: `scale(${zoom / 100})`, height: `${10000 / zoom}%`, width: `${10000 / zoom}%` }}
          >
            <iframe
              src={fileUrl}
              title="PDF File Preview"
              className="w-full h-full border-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 px-6 py-4 border-t border-white/5 bg-slate-950/40 rounded-b-3xl shrink-0">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl transition text-xs font-bold cursor-pointer text-gray-300"
          >
            Close Preview
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default ResumePreviewModal
