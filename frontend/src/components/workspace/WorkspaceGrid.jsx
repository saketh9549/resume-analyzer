import React from "react"
import { Search, Filter, ChevronDown } from "lucide-react"
import ResumeCard from "./ResumeCard"
import { useResumeMenu } from "../../hooks/useResumeMenu"

const CATEGORIES = ["All", "Software", "Product Management", "Marketing", "Others"]

function WorkspaceGrid({
  uploads,
  searchQuery,
  setSearchQuery,
  scoreFilter,
  setScoreFilter,
  sortBy,
  setSortBy,
  selectedCategory,
  setSelectedCategory,
  pinnedIds,
  categories,
  onTogglePin,
  onCategoryChange,
  onOpenPreview,
  onAiRewrite,
  onMockInterview,
  onVisualAudit,
  onReScore,
  onRename,
  onDownload,
  onDelete,
  onAnalyze,
  actionLoadingId
}) {
  const { activeMenuId, toggleMenu, registerRef } = useResumeMenu()

  // Filter & Sort Logic
  const filteredUploads = uploads
    .filter((item) => {
      const matchSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase())
      
      const scoreVal = parseInt(item.score) || 0
      let matchScore = true
      if (scoreFilter === "high") matchScore = scoreVal >= 80
      else if (scoreFilter === "mid") matchScore = scoreVal >= 60 && scoreVal < 80
      else if (scoreFilter === "low") matchScore = scoreVal < 60

      const category = categories[item.id] || "Others"
      let matchCategory = true
      if (selectedCategory !== "All") {
        matchCategory = category === selectedCategory
      }

      return matchSearch && matchScore && matchCategory
    })
    .sort((a, b) => {
      // Pinned items stay on top
      const aPinned = pinnedIds.includes(a.id)
      const bPinned = pinnedIds.includes(b.id)
      if (aPinned && !bPinned) return -1
      if (!aPinned && bPinned) return 1

      if (sortBy === "score") {
        return (parseInt(b.score) || 0) - (parseInt(a.score) || 0)
      } else if (sortBy === "name") {
        return a.name.localeCompare(b.name)
      } else {
        return new Date(b.date) - new Date(a.date)
      }
    })

  return (
    <div className="space-y-6">
      {/* Filters bar */}
      <div className="flex flex-col lg:flex-row gap-4 justify-between items-stretch lg:items-center pb-6 border-b border-white/5">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-4 top-3.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search resumes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-2xl pl-12 pr-5 py-3 text-sm text-gray-200 outline-none focus:border-blue-500 transition"
          />
        </div>

        {/* Filters Group */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Score filter */}
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3.5 py-2.5 rounded-2xl text-xs font-semibold">
            <Filter size={14} className="text-blue-400" />
            <select
              value={scoreFilter}
              onChange={(e) => setScoreFilter(e.target.value)}
              className="bg-transparent text-gray-200 outline-none cursor-pointer border-none p-0 pr-4 focus:ring-0"
            >
              <option value="all" className="bg-slate-950">All Scores</option>
              <option value="high" className="bg-slate-950">High (≥80%)</option>
              <option value="mid" className="bg-slate-950">Intermediate (60-79%)</option>
              <option value="low" className="bg-slate-950">Needs Work (&lt;60%)</option>
            </select>
          </div>

          {/* Sort dropdown */}
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3.5 py-2.5 rounded-2xl text-xs font-semibold">
            <ChevronDown size={14} className="text-blue-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent text-gray-200 outline-none cursor-pointer border-none p-0 pr-4 focus:ring-0"
            >
              <option value="date" className="bg-slate-950">Sort by Date</option>
              <option value="score" className="bg-slate-950">Sort by ATS Score</option>
              <option value="name" className="bg-slate-950">Sort by Name</option>
            </select>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`
              px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap cursor-pointer
              ${selectedCategory === cat 
                ? "bg-blue-500/10 border border-blue-500/20 text-blue-400" 
                : "bg-white/5 border border-white/5 text-gray-400 hover:text-gray-200"
              }
            `}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Resumes Grid */}
      {filteredUploads.length === 0 ? (
        <div className="text-center py-16 text-gray-400 bg-slate-950/30 border border-white/5 rounded-3xl">
          <p className="mb-4 text-base font-medium">No resumes match the selected parameters.</p>
          <button
            onClick={() => {
              setSearchQuery("")
              setScoreFilter("all")
              setSelectedCategory("All")
            }}
            className="text-blue-400 hover:text-blue-300 underline text-sm cursor-pointer"
          >
            Reset query filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredUploads.map((item) => (
            <ResumeCard
              key={item.id}
              item={item}
              isPinned={pinnedIds.includes(item.id)}
              category={categories[item.id] || "Others"}
              onTogglePin={onTogglePin}
              onOpenPreview={() => onOpenPreview(item.id, item.name)}
              onAiRewrite={() => onAiRewrite(item.id)}
              onMockInterview={() => onMockInterview(item.id)}
              onVisualAudit={() => onVisualAudit(item.id)}
              onReScore={() => onReScore(item.id)}
              onRename={() => onRename(item.id, item.name)}
              onDownload={() => onDownload(item.id, item.name)}
              onDelete={() => onDelete(item.id)}
              onCategoryChange={(cat) => onCategoryChange(item.id, cat)}
              isOpen={activeMenuId === item.id}
              onToggle={() => toggleMenu(item.id)}
              registerRef={(el) => registerRef(item.id, el)}
              onAnalyze={onAnalyze}
              isLoading={actionLoadingId === item.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default WorkspaceGrid
