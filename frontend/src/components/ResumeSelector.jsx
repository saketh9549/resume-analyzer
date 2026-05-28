import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Search, ChevronDown, Check } from 'lucide-react'
import { useResume } from '../context/ResumeContext'

export function ResumeSelector() {
  const { resumes, activeResume, setActiveResume, loading } = useResume()
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredResumes = resumes.filter(r => 
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (r.category && r.category.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleSelect = (resume) => {
    setActiveResume(resume)
    setIsOpen(false)
  }

  return (
    <div className="relative z-40">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between gap-3 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 px-5 py-3 rounded-2xl backdrop-blur-md transition-all text-left w-64 cursor-pointer"
      >
        <div className="flex items-center gap-3 overflow-hidden">
          <FileText size={18} className="text-blue-400 flex-shrink-0" />
          <div className="overflow-hidden">
            {activeResume ? (
              <>
                <p className="text-sm font-semibold text-gray-200 truncate">{activeResume.name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">
                    {activeResume.score}
                  </span>
                  <span className="text-[10px] text-gray-400 truncate">
                    {activeResume.category || 'General'}
                  </span>
                </div>
              </>
            ) : (
              <p className="text-sm font-semibold text-gray-400">Select Resume...</p>
            )}
          </div>
        </div>
        <ChevronDown size={16} className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.15 }}
            className="absolute left-0 right-0 mt-2 bg-slate-900 border border-white/10 rounded-2xl shadow-xl backdrop-blur-lg overflow-hidden flex flex-col w-64 max-h-80"
          >
            {/* Search Input */}
            <div className="p-3 border-b border-white/5 flex items-center gap-2 bg-white/5">
              <Search size={14} className="text-gray-400" />
              <input
                type="text"
                placeholder="Search resumes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-xs text-gray-200 outline-none w-full border-none focus:ring-0 focus:outline-none"
              />
            </div>

            {/* List */}
            <div className="overflow-y-auto py-1 scrollbar-thin max-h-60">
              {loading ? (
                <div className="p-4 text-center text-xs text-gray-500">Loading...</div>
              ) : filteredResumes.length === 0 ? (
                <div className="p-4 text-center text-xs text-gray-500">No resumes found</div>
              ) : (
                filteredResumes.map((r) => {
                  const isActive = activeResume && activeResume.id === r.id
                  return (
                    <button
                      key={r.id}
                      onClick={() => handleSelect(r)}
                      className={`flex items-center justify-between w-full text-left px-4 py-3 hover:bg-white/5 transition-all border-b border-white/5 last:border-b-0 cursor-pointer ${
                        isActive ? 'bg-blue-500/10' : ''
                      }`}
                    >
                      <div className="overflow-hidden pr-2">
                        <p className="text-xs font-semibold text-gray-200 truncate">{r.name}</p>
                        <div className="flex items-center gap-1.5 mt-1">
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">
                            {r.score}
                          </span>
                          <span className="text-[9px] text-gray-400 truncate">
                            {r.category || 'General'}
                          </span>
                        </div>
                      </div>
                      {isActive && <Check size={14} className="text-blue-400 flex-shrink-0" />}
                    </button>
                  )
                })
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ResumeSelector
