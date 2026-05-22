function Card(props) {
  return (
    <div className="bg-slate-900 p-6 rounded-2xl hover:bg-slate-800 transition">

      <h2 className="text-gray-400">
        {props.title}
      </h2>

      <p className="text-4xl font-bold mt-2">
        {props.value}
      </p>

    </div>
  )
}

export default Card