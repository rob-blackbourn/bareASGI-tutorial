import React from 'react'
import PropTypes from 'prop-types'
import { Redirect } from 'react-router-dom'
import { withStyles } from '@material-ui/core/styles'
import Typography from '@material-ui/core/Typography'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'
import PostEditor from './PostEditor'
import { API_PATH } from '../config'

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
    isUpdated: false,
    error: null
  }

  handleUpdate = () => {
    const { post } = this.state
    const { id, title, description, content } = post
    const url = `${API_PATH}/${id}`

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
          this.setState({ error: 'Unable to update post' })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to update post' })
      })
  }

  componentDidMount () {
    const { match } = this.props
    const url = `${API_PATH}/${match.params.id}`
    fetch(url)
      .then(response => {
        if (response.ok) {
          response.json()
            .then(post => {
              this.setState({ post })
            })
            .catch(() => {
              this.setState({ error: 'Unable to read post' })
            })
        }
      })
      .catch(() => {
        this.setState({ error: 'Unable to read post' })
      })
  }

  handleChange = (post, key, value) => {
    this.setState({ post: { ...post, [key]: value } })
  }

  handleDismissDialog = () => {
    this.setState({ error: null })
  }

  renderRedirect = () => {
    return <Redirect to='/blog/ui/index' />
  }

  renderDialog = () => {
    return (
      <Dialog onClose={() => this.handleDismissDialog()} open={this.state.error !== null}>
        <DialogTitle>Error</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Unable to save post
          </DialogContentText>
          <DialogActions>
            <Button onClick={() => this.handleDismissDialog()} color='primary'>
              Dismiss
            </Button>
          </DialogActions>
        </DialogContent>
      </Dialog>
    )
  }

  renderContent = () => {
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

  render () {
    if (this.state.isUpdated === true) {
      return this.renderRedirect()
    } else if (this.state.error) {
      return this.renderDialog()
    } else {
      return this.renderContent()
    }
  }
}

EditPost.apply.propTypes = {
  classes: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired
}

export default withStyles(styles)(EditPost)
