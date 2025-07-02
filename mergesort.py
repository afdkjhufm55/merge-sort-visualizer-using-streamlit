import streamlit as st
import time
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import random

# Configure page
st.set_page_config(
    page_title="Merge Sort Visualizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .main-header {
        text-align: center;
        color: #ff6b6b;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
    }
    
    .sub-header {
        text-align: center;
        color: #4ecdc4;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .step-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        color: white;
    }
    
    .stNumberInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border: 2px solid #4ecdc4;
        border-radius: 5px;
    }
    
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
        border: 2px solid #4ecdc4;
        border-radius: 5px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
</style>
""", unsafe_allow_html=True)

class MergeSortVisualizer:
    def _init_(self):
        self.array = []
        self.steps = []
        self.colors = px.colors.qualitative.Set3
        
    def merge_sort_with_steps(self, arr, start_idx=0, level=0):
        """Merge sort with step tracking for visualization"""
        if len(arr) <= 1:
            return arr
            
        # Record the split step
        mid = len(arr) // 2
        left_part = arr[:mid]
        right_part = arr[mid:]
        
        self.steps.append({
            'type': 'split',
            'array': self.array.copy(),
            'left': [start_idx + i for i in range(len(left_part))],
            'right': [start_idx + mid + i for i in range(len(right_part))],
            'level': level,
            'description': f'Splitting array at position {mid}'
        })
        
        # Recursively sort both halves
        left_sorted = self.merge_sort_with_steps(left_part, start_idx, level + 1)
        right_sorted = self.merge_sort_with_steps(right_part, start_idx + mid, level + 1)
        
        # Merge the sorted halves
        merged = self.merge_with_steps(left_sorted, right_sorted, start_idx, level)
        
        return merged
    
    def merge_with_steps(self, left, right, start_idx, level):
        """Merge two sorted arrays with step tracking"""
        result = []
        i = j = 0
        result_idx = start_idx
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                self.array[result_idx] = left[i]
                i += 1
            else:
                result.append(right[j])
                self.array[result_idx] = right[j]
                j += 1
            
            result_idx += 1
            
            # Record merge step
            self.steps.append({
                'type': 'merge',
                'array': self.array.copy(),
                'comparing': [start_idx + len(result) - 1],
                'level': level,
                'description': f'Merging: placed {result[-1]} at position {result_idx - 1}'
            })
        
        # Add remaining elements
        while i < len(left):
            result.append(left[i])
            self.array[result_idx] = left[i]
            self.steps.append({
                'type': 'merge',
                'array': self.array.copy(),
                'comparing': [result_idx],
                'level': level,
                'description': f'Adding remaining element {left[i]}'
            })
            i += 1
            result_idx += 1
        
        while j < len(right):
            result.append(right[j])
            self.array[result_idx] = right[j]
            self.steps.append({
                'type': 'merge',
                'array': self.array.copy(),
                'comparing': [result_idx],
                'level': level,
                'description': f'Adding remaining element {right[j]}'
            })
            j += 1
            result_idx += 1
        
        return result
    
    def create_visualization(self, step_data, title="", show_previous=False, viz_types=['Bars', 'Nodes']):
        """Create visualization based on user-selected types"""
        n = len(step_data['array'])
        rows = 2 if show_previous and step_data.get('previous_step') else 1
        cols = len(viz_types)
        
        # Define subplot specs based on visualization types
        specs = [[{'type': 'bar' if v == 'Bars' else 'scatter'} for v in viz_types]] * rows
        subplot_titles = []
        for r in range(rows):
            for v in viz_types:
                if r == 0:
                    subplot_titles.append(title if v == viz_types[0] else "")
                else:
                    subplot_titles.append(f"Previous Step ({v})" if v == viz_types[0] else "")
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            specs=specs,
            vertical_spacing=0.1,
            horizontal_spacing=0.05
        )
        
        def add_step_visualization(step, row, is_previous=False):
            values = step['array']
            colors = ['#4ecdc4'] * n  # Default cyan
            sizes = [30] * n  # Default node size
            
            if step['type'] == 'split':
                for idx in step.get('left', []):
                    if idx < len(colors):
                        colors[idx] = '#ff6b6b'  # Red for left
                for idx in step.get('right', []):
                    if idx < len(colors):
                        colors[idx] = '#ffa500'  # Orange for right
            elif step['type'] == 'merge':
                for idx in step.get('comparing', []):
                    if idx < len(colors):
                        colors[idx] = '#00ff00'  # Green for current merge
                        sizes[idx] = 40  # Larger size for animation
            
            for col_idx, viz_type in enumerate(viz_types, 1):
                if viz_type == 'Bars':
                    # Add bar chart
                    fig.add_trace(
                        go.Bar(
                            x=list(range(n)),
                            y=values,
                            marker=dict(
                                color=colors,
                                line=dict(color='white', width=2)
                            ),
                            text=values,
                            textposition='outside',
                            textfont=dict(size=14, color='white')
                        ),
                        row=row,
                        col=col_idx
                    )
                else:
                    # Add circular nodes with gaps
                    x_positions = [i * 1.2 for i in range(n)]  # Add gaps by scaling x-coordinates
                    fig.add_trace(
                        go.Scatter(
                            x=x_positions,
                            y=[max(values) * 1.2] * n,
                            mode='markers+text',
                            marker=dict(
                                size=sizes,
                                color=colors,
                                line=dict(color='white', width=2),
                                symbol='circle',
                                opacity=0.9
                            ),
                            text=values,
                            textposition='middle center',
                            textfont=dict(size=12, color='white'),
                            hoverinfo='text',
                            hovertext=[f'Value: {v}' for v in values]
                        ),
                        row=row,
                        col=col_idx
                    )
        add_step_visualization(step_data, row=1)
        if show_previous and step_data.get('previous_step'):
            add_step_visualization(step_data['previous_step'], row=2, is_previous=True)
        
        layout_updates = {
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': dict(color='white'),
            'showlegend': False,
            'height': 800 if show_previous and step_data.get('previous_step') else 400,
            'margin': dict(l=50, r=50, t=50, b=50)
        }
        
        for row in range(1, rows + 1):
            for col_idx, viz_type in enumerate(viz_types, 1):
                axis_num = (row - 1) * cols + col_idx
                xaxis = f'xaxis{axis_num}' if axis_num > 1 else 'xaxis'
                yaxis = f'yaxis{axis_num}' if axis_num > 1 else 'yaxis'
                
                layout_updates[xaxis] = dict(
                    title="Index",
                    showgrid=False,
                    color='white',
                    tickfont=dict(color='white')
                )
                layout_updates[yaxis] = dict(
                    title="Value",
                    showgrid=(viz_type == 'Bars'),
                    gridcolor='rgba(255,255,255,0.1)' if viz_type == 'Bars' else None,
                    color='white',
                    tickfont=dict(color='white'),
                    range=[0, max(step_data['array']) * 1.5] if viz_type == 'Nodes' else None
                )
        
        fig.update_layout(**layout_updates)
        
        if 'Nodes' in viz_types:
            fig.update_traces(
                marker=dict(
                    sizemode='diameter',
                    sizeref=0.5
                ),
                selector=dict(type='scatter')
            )
        
        return fig

def main():
    st.markdown('<h1 class="main-header"> Merge Sort Visualizer</h1>', unsafe_allow_html=True)
    
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = MergeSortVisualizer()
    if 'array_created' not in st.session_state:
        st.session_state.array_created = False
    if 'sorting_done' not in st.session_state:
        st.session_state.sorting_done = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if 'viz_types' not in st.session_state:
        st.session_state.viz_types = ['Bars', 'Nodes']
    
    with st.sidebar:
        st.markdown("### Configuration")
        
        num_nodes = st.number_input(
            "Number of Elements:",
            min_value=2,
            max_value=20,
            value=8,
            help="Choose between 2-20 elements"
        )
        
        st.markdown("### Visualization Type")
        st.session_state.viz_types = st.multiselect(
            "Select Visualization(s):",
            options=['Bars', 'Nodes'],
            default=st.session_state.viz_types,
            help="Choose Bars, Nodes, or both"
        )
        
        if not st.session_state.viz_types:
            st.error("Please select at least one visualization type!")
            st.session_state.viz_types = ['Bars']
        
        st.markdown("---")
        
        input_method = st.radio(
            "Input Method:",
            ["Manual Input", "Random Generation"]
        )
        
        if input_method == "Manual Input":
            st.markdown("### Enter Values")
            array_input = st.text_input(
                "Enter values (comma-separated):",
                placeholder="e.g., 64, 34, 25, 12, 22, 11, 90",
                help=f"Enter exactly {num_nodes} numbers separated by commas"
            )
            
            if st.button("Create Array"):
                try:
                    if array_input.strip():
                        values = [int(x.strip()) for x in array_input.split(',')]
                        if len(values) != num_nodes:
                            st.error(f"Please enter exactly {num_nodes} values!")
                        else:
                            st.session_state.visualizer.array = values
                            st.session_state.array_created = True
                            st.session_state.sorting_done = False
                            st.session_state.current_step = 0
                            st.session_state.is_playing = False
                            st.success("Array created successfully!")
                    else:
                        st.error("Please enter some values!")
                except ValueError:
                    st.error("Please enter valid integers only!")
        
        else:  
            if st.button("Generate Random Array"):
                random_values = [random.randint(1, 100) for _ in range(num_nodes)]
                st.session_state.visualizer.array = random_values
                st.session_state.array_created = True
                st.session_state.sorting_done = False
                st.session_state.current_step = 0
                st.session_state.is_playing = False
                st.success("Random array generated!")
        
        st.markdown("---")
        
        if st.session_state.array_created:
            st.markdown("### Controls")
            
            if st.button("Start Merge Sort"):
                if not st.session_state.sorting_done:
                    with st.spinner("Analyzing sorting steps..."):
                        st.session_state.visualizer.steps = []
                        original_array = st.session_state.visualizer.array.copy()
                        st.session_state.visualizer.merge_sort_with_steps(original_array)
                        st.session_state.sorting_done = True
                        st.session_state.current_step = 0
                        st.session_state.is_playing = False
                    st.success("Ready to visualize!")
            
            if st.button("Reset"):
                st.session_state.array_created = False
                st.session_state.sorting_done = False
                st.session_state.current_step = 0
                st.session_state.is_playing = False
                st.session_state.visualizer = MergeSortVisualizer()
                st.rerun()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.array_created:
            # Display current array
            st.markdown("### Current Array Visualization")
            
            if not st.session_state.sorting_done:
                # Show initial array
                initial_step = {
                    'type': 'initial',
                    'array': st.session_state.visualizer.array,
                    'description': 'Initial unsorted array'
                }
                fig = st.session_state.visualizer.create_visualization(
                    initial_step, 
                    "Initial Array - Ready to Sort",
                    viz_types=st.session_state.viz_types
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.info(f"Array: {st.session_state.visualizer.array}")
            
            else:
                # Show sorting visualization
                if st.session_state.visualizer.steps:
                    # Animation controls
                    col_prev, col_play, col_pause, col_next, col_speed = st.columns([1, 1, 1, 1, 2])
                    
                    with col_prev:
                        if st.button("<-Previous"):
                            if st.session_state.current_step > 0:
                                st.session_state.current_step -= 1
                                st.session_state.is_playing = False
                                st.rerun()
                    
                    with col_play:
                        if st.button("▶ Play" if not st.session_state.is_playing else "▶ Resume"):
                            st.session_state.is_playing = True
                    
                    with col_pause:
                        if st.button("⏸ Pause"):
                            st.session_state.is_playing = False
                    
                    with col_next:
                        if st.button("Next->"):
                            if st.session_state.current_step < len(st.session_state.visualizer.steps) - 1:
                                st.session_state.current_step += 1
                                st.session_state.is_playing = False
                                st.rerun()
                    
                    with col_speed:
                        st.markdown("*Animation Speed*")
                        speed = st.slider(
                            "Speed (seconds per step)",
                            0.1,
                            2.0,
                            1.0,
                            label_visibility="collapsed"
                        )
                    
                    # Step navigation
                    st.markdown("*Step Navigation*")
                    st.session_state.current_step = st.slider(
                        "Step",
                        0,
                        len(st.session_state.visualizer.steps) - 1,
                        st.session_state.current_step,
                        label_visibility="collapsed"
                    )
                    
                    # Play animation if active
                    if st.session_state.is_playing:
                        progress_bar = st.progress(0)
                        step_placeholder = st.empty()
                        chart_placeholder = st.empty()
                        
                        while st.session_state.is_playing and st.session_state.current_step < len(st.session_state.visualizer.steps):
                            current_step_data = st.session_state.visualizer.steps[st.session_state.current_step]
                            if st.session_state.current_step > 0:
                                current_step_data['previous_step'] = st.session_state.visualizer.steps[st.session_state.current_step - 1]
                            
                            progress_bar.progress((st.session_state.current_step + 1) / len(st.session_state.visualizer.steps))
                            
                            fig = st.session_state.visualizer.create_visualization(
                                current_step_data, 
                                f"Step {st.session_state.current_step + 1}: {current_step_data['description']}",
                                show_previous=True,
                                viz_types=st.session_state.viz_types
                            )
                            chart_placeholder.plotly_chart(fig, use_container_width=True)
                            step_placeholder.markdown(f'<div class="step-info">Step {st.session_state.current_step + 1}: {current_step_data["description"]}</div>', unsafe_allow_html=True)
                            
                            time.sleep(speed)
                            st.session_state.current_step += 1
                            if st.session_state.current_step >= len(st.session_state.visualizer.steps):
                                st.session_state.is_playing = False
                                break
                        
                        progress_bar.empty()
                        if not st.session_state.is_playing and st.session_state.current_step >= len(st.session_state.visualizer.steps):
                            st.success("🎉 Sorting completed!")
                    
                    # Show current step
                    if 0 <= st.session_state.current_step < len(st.session_state.visualizer.steps):
                        current_step_data = st.session_state.visualizer.steps[st.session_state.current_step]
                        if st.session_state.current_step > 0:
                            current_step_data['previous_step'] = st.session_state.visualizer.steps[st.session_state.current_step - 1]
                        
                        fig = st.session_state.visualizer.create_visualization(
                            current_step_data,
                            f"Step {st.session_state.current_step + 1}: {current_step_data['description']}",
                            show_previous=True,
                            viz_types=st.session_state.viz_types
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Step information
                        st.markdown(f'<div class="step-info">Step {st.session_state.current_step + 1} of {len(st.session_state.visualizer.steps)}: {current_step_data["description"]}</div>', unsafe_allow_html=True)
                
                # Final result
                if st.session_state.current_step == len(st.session_state.visualizer.steps) - 1:
                    st.success("Array is now sorted!")
                    st.balloons()
        
        else:
            # Welcome message
            st.markdown("""
            ### Welcome to Merge Sort Visualizer!
            
            *Steps to get started:*
            1. Set the number of elements in the sidebar
            2. Select visualization type (Bars, Nodes, or both)
            3. Choose your input method (Manual or Random)
            4. Create your array
            5. Start the merge sort visualization
            6. Use controls to navigate through steps
            
            *Color Legend:*
            - 🔴 *Red*: Left partition during split
            - 🟠 *Orange*: Right partition during split  
            - 🟢 *Green*: Currently being merged
            - 🔵 *Cyan*: Default/sorted elements
            
            *Visualizations:*
            - 📊 Bars: Bar chart showing values
            - ⚪ Nodes: Circular nodes with values and animations
            """)
    
    with col2:
        if st.session_state.array_created:
            st.markdown("### Statistics")
            
            array_stats = {
                "Elements": len(st.session_state.visualizer.array),
                "Min Value": min(st.session_state.visualizer.array),
                "Max Value": max(st.session_state.visualizer.array)
            }
            
            for key, value in array_stats.items():
                st.metric(key, value)
            
            if st.session_state.sorting_done:
                st.markdown("### Algorithm Info")
                st.info(f"*Total Steps:* {len(st.session_state.visualizer.steps)}")
                st.info(f"*Time Complexity:* O(n log n)")
                st.info(f"*Space Complexity:* O(n)")
                st.info(f"*Algorithm:* Divide & Conquer")

if __name__ == "__main__":
    main()