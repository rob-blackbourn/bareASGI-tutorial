import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles'
import Typography from '@material-ui/core/Typography'
import PostEditor from './PostEditor'

const styles = theme => ({
  root: {}
})

class CreatePost extends React.Component {
  state = {
    post: {
      title: '',
      description: '',
      content: ''
    },
    isCreated: false
  }

  handleCreate = () => {
    const { post } = this.state

    fetch('http://localhost:9501/blog/api/blog_entry', {
      method: 'POST',
      body: JSON.stringify({ ...post }),
      headers: new Headers([
        ['content-type', 'application/json']
      ])
    })
      .then(response => {
        if (response.ok) {
          this.setState({ isCreated: true })
          console.log('Created')
        } else {
          console.log('Failed')
        }
      })
      .catch(error => {
        console.log(error)
      })
  }

  handleChange = (post, key, value) => {
    this.setState({
      post: {
        ...post,
        [key]: value
      }
    })
  }

  render () {
    if (this.state.isCreated === true) {
      return <Redirect to='/blog/ui/index' />
    }

    const { classes } = this.props
    const { post } = this.state

    return (
      <div>
        <Typography variant='h2'>New Post</Typography>

        <PostEditor
          className={classes.root}
          title={post.title}
          onTitleChange={value => this.handleChange(post, 'title', value)}
          description={post.description}
          onDescriptionChange={value => this.handleChange(post, 'description', value)}
          content={post.content}
          onContentChange={value => this.handleChange(post, 'content', value)}
          onSubmit={this.handleCreate}
          submitContent='Create'
        />
      </div>
    )
  }
}

CreatePost.apply.propTypes = {
  classes: PropTypes.object.isRequired
}

export default withStyles(styles)(CreatePost)
