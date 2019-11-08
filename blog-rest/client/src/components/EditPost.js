import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles'
import Typography from '@material-ui/core/Typography'
import PostEditor from './PostEditor'

const styles = theme => ({
  root: {}
})

class EditPost extends React.Component {
  state = {
    post: {
      title: '',
      description: '',
      content: ''
    },
    isUpdated: false
  }

  handleUpdate = () => {
    const { post } = this.state
    const { id, title, description, content } = post
    const url = `http://localhost:9501/blog/api/blog_entry/${id}`

    fetch(url, {
      method: 'POST',
      body: JSON.stringify({
        title,
        description,
        content
      }),
      headers: new Headers([
        ['content-type', 'application/json']
      ])
    })
      .then(response => {
        if (response.ok) {
          this.setState({ isUpdated: true })
        } else {
          console.log('Failed')
        }
      })
      .catch(error => {
        console.log(error)
      })
  }

  componentDidMount () {
    const { match } = this.props
    const url = `http://localhost:9501/blog/api/blog_entry/${match.params.id}`
    fetch(url)
      .then(response => {
        if (response.ok) {
          response.json()
            .then(post => {
              this.setState({ post })
            })
            .catch(error => {
              console.log(error)
            })
        }
      })
      .catch(error => {
        console.log(error)
      })
  }

  handleChange = (post, key, value) => {
    this.setState({ post: { ...post, [key]: value } })
  }

  render () {
    if (this.state.isUpdated === true) {
      return <Redirect to='/blog/ui/index' />
    }

    const { classes } = this.props
    const { post } = this.state

    return (
      <div>
        <Typography variant='h2'>Update Post</Typography>

        <PostEditor
          className={classes.root}
          title={post.title}
          onTitleChange={value => this.handleChange(post, 'title', value)}
          description={post.description}
          onDescriptionChange={value => this.handleChange(post, 'description', value)}
          content={post.content}
          onContentChange={value => this.handleChange(post, 'content', value)}
          onSubmit={this.handleUpdate}
          submitContent='Save'
        />
      </div>
    )
  }
}

EditPost.apply.propTypes = {
  classes: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired
}

export default withStyles(styles)(EditPost)
